"""边端接入、受控文件保存、模拟分析和本地 outbox。"""

from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Protocol, cast

from edge_service.normalization import normalize_metadata

logger = logging.getLogger(__name__)
UTC = timezone.utc
MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_MODALITIES = frozenset({"infrared", "acoustic", "partial_discharge"})
ALLOWED_FILE_TYPES = {
    "application/json": frozenset({".json"}),
    "application/octet-stream": frozenset({".bin"}),
    "audio/wav": frozenset({".wav"}),
    "image/jpeg": frozenset({".jpg", ".jpeg"}),
    "image/png": frozenset({".png"}),
}


class FileValidationError(ValueError):
    """客户端文件不符合边端安全边界。"""


class CloudValidationError(ValueError):
    """云端返回不可自动重试的校验或鉴权错误。"""


class OutboxStatus(str, Enum):
    PENDING = "PENDING"
    SENDING = "SENDING"
    RETRYABLE = "RETRYABLE"
    FAILED = "FAILED"
    SENT = "SENT"


@dataclass(frozen=True)
class CloudResponse:
    accepted: bool
    retryable: bool = False
    message: str = ""

    @classmethod
    def ok(cls) -> CloudResponse:
        return cls(accepted=True)


class CloudClient(Protocol):
    def send_diagnostic(self, payload: dict[str, object]) -> CloudResponse: ...


def _parse_utc(value: object) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("时间必须是带 Z 后缀的 UTC ISO-8601 时间")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as error:
        raise ValueError("时间不是有效的 UTC ISO-8601 时间") from error
    if parsed.tzinfo is None:
        raise ValueError("时间必须带 UTC 时区")
    return parsed.astimezone(UTC)


def _format_utc(value: datetime) -> str:
    if value.tzinfo is None:
        raise ValueError("时间必须带 UTC 时区")
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _validate_detection_metadata(metadata: Mapping[str, object]) -> dict[str, object]:
    normalized_ids = normalize_metadata(metadata)
    modality = metadata.get("modality")
    if modality not in ALLOWED_MODALITIES:
        raise ValueError("模态不在允许范围内")
    captured_at = _parse_utc(metadata.get("capturedAt"))
    if not metadata.get("site"):
        raise ValueError("site is required")
    return {
        **metadata,
        **normalized_ids,
        "modality": cast(str, modality),
        "capturedAt": _format_utc(captured_at),
    }


def _validate_heartbeat(payload: Mapping[str, object]) -> dict[str, str]:
    for key in ("terminalId", "edgeId", "modality"):
        value = payload.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} is required")
    modality = payload["modality"]
    if modality not in ALLOWED_MODALITIES:
        raise ValueError("模态不在允许范围内")
    _parse_utc(payload.get("sentAt"))
    return {
        "terminalId": cast(str, payload["terminalId"]),
        "edgeId": cast(str, payload["edgeId"]),
        "modality": cast(str, modality),
    }


class _Outbox:
    def __init__(self, database_path: Path) -> None:
        database_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(database_path, check_same_thread=False)
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS edge_outbox (
                event_id TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                status TEXT NOT NULL,
                retry_count INTEGER NOT NULL DEFAULT 0,
                next_retry_at TEXT,
                last_error TEXT
            )
            """
        )
        self.connection.commit()

    def get(self, event_id: str) -> tuple[OutboxStatus, dict[str, object]] | None:
        row = self.connection.execute(
            "SELECT status, payload FROM edge_outbox WHERE event_id = ?", (event_id,)
        ).fetchone()
        if row is None:
            return None
        return OutboxStatus(row[0]), cast(dict[str, object], json.loads(row[1]))

    def enqueue(
        self, event_id: str, payload: dict[str, object], status: OutboxStatus
    ) -> None:
        self.connection.execute(
            "INSERT OR IGNORE INTO edge_outbox(event_id, payload, status) VALUES (?, ?, ?)",
            (event_id, json.dumps(payload, ensure_ascii=False), status.value),
        )
        self.connection.commit()

    def due(self, now: datetime) -> list[tuple[str, dict[str, object]]]:
        rows = self.connection.execute(
            """
            SELECT event_id, payload FROM edge_outbox
            WHERE status IN (?, ?) AND (next_retry_at IS NULL OR next_retry_at <= ?)
            ORDER BY event_id
            """,
            (
                OutboxStatus.PENDING.value,
                OutboxStatus.RETRYABLE.value,
                _format_utc(now),
            ),
        ).fetchall()
        return [(row[0], cast(dict[str, object], json.loads(row[1]))) for row in rows]

    def mark_sent(self, event_id: str) -> None:
        self.connection.execute(
            "UPDATE edge_outbox SET status = ?, last_error = NULL WHERE event_id = ?",
            (OutboxStatus.SENT.value, event_id),
        )
        self.connection.commit()

    def mark_retryable(self, event_id: str, now: datetime, error: str) -> None:
        self.connection.execute(
            """
            UPDATE edge_outbox
            SET status = ?, retry_count = retry_count + 1, next_retry_at = ?, last_error = ?
            WHERE event_id = ?
            """,
            (
                OutboxStatus.RETRYABLE.value,
                _format_utc(now + timedelta(seconds=30)),
                error,
                event_id,
            ),
        )
        self.connection.commit()

    def mark_failed(self, event_id: str, error: str) -> None:
        self.connection.execute(
            "UPDATE edge_outbox SET status = ?, last_error = ? WHERE event_id = ?",
            (OutboxStatus.FAILED.value, error, event_id),
        )
        self.connection.commit()


class EdgeService:
    def __init__(self, storage_root: Path, outbox_path: Path | None = None) -> None:
        self.storage_root = storage_root
        self.storage_root.mkdir(parents=True, exist_ok=True)
        self.outbox = _Outbox(outbox_path or storage_root / "outbox.sqlite3")
        self.terminal_states: dict[str, dict[str, str]] = {}

    def receive_heartbeat(
        self, payload: Mapping[str, object], received_at: datetime
    ) -> dict[str, str]:
        normalized = _validate_heartbeat(payload)
        result = {
            **normalized,
            "lastSeenAt": _format_utc(received_at),
            "status": "ONLINE",
        }
        self.terminal_states[normalized["terminalId"]] = result
        return result

    def receive_detection(
        self,
        metadata: Mapping[str, object],
        original_filename: str,
        content_type: str,
        content: bytes,
    ) -> dict[str, object]:
        normalized = _validate_detection_metadata(metadata)
        suffix = self._validate_file(original_filename, content_type, content)
        event_id = str(normalized["eventId"])
        existing = self.outbox.get(event_id)
        if existing is not None:
            return existing[1]

        event_directory = self.storage_root / event_id
        event_directory.mkdir(parents=True, exist_ok=False)
        stored_path = event_directory / f"payload{suffix}"
        stored_path.write_bytes(content)
        digest = hashlib.sha256(content).hexdigest()
        base_result: dict[str, object] = {
            **normalized,
            "storedPath": str(stored_path),
            "evidenceUri": f"s3://edge-evidence/events/{event_id}{suffix}",
            "sha256": digest,
        }
        if not content:
            result = {
                **base_result,
                "status": OutboxStatus.FAILED.value,
                "errorCode": "EMPTY_FILE",
            }
            self.outbox.enqueue(event_id, result, OutboxStatus.FAILED)
            logger.error("模拟分析失败 eventId=%s errorCode=EMPTY_FILE", event_id)
            return result

        result = {
            **base_result,
            "status": OutboxStatus.PENDING.value,
            "defectType": "thermal-anomaly"
            if normalized["modality"] == "infrared"
            else "signal-anomaly",
            "confidence": 0.91,
            "severity": "medium",
            "analyzedAt": _format_utc(datetime.now(UTC)),
        }
        self.outbox.enqueue(event_id, result, OutboxStatus.PENDING)
        logger.info(
            "检测事件已保存 eventId=%s assetId=%s terminalId=%s edgeId=%s",
            event_id,
            normalized["assetId"],
            normalized["terminalId"],
            normalized["edgeId"],
        )
        return result

    def flush_outbox(self, client: CloudClient, now: datetime) -> None:
        for event_id, payload in self.outbox.due(now):
            try:
                response = client.send_diagnostic(payload)
                if response.accepted:
                    self.outbox.mark_sent(event_id)
                elif response.retryable:
                    self.outbox.mark_retryable(event_id, now, response.message)
                else:
                    self.outbox.mark_failed(event_id, response.message)
            except CloudValidationError as error:
                self.outbox.mark_failed(event_id, str(error))
                logger.error("云端校验失败且不重试 eventId=%s", event_id)
            except (ConnectionError, TimeoutError, OSError) as error:
                self.outbox.mark_retryable(event_id, now, str(error))
                logger.warning("云端暂不可达，保留待上报事件 eventId=%s", event_id)

    def outbox_status(self, event_id: str) -> OutboxStatus | None:
        record = self.outbox.get(event_id)
        return record[0] if record is not None else None

    @staticmethod
    def _validate_file(
        original_filename: str, content_type: str, content: bytes
    ) -> str:
        path = Path(original_filename)
        if (
            not original_filename
            or "\x00" in original_filename
            or path.name != original_filename
            or path.name in {".", ".."}
        ):
            raise FileValidationError("文件名包含路径或控制字符")
        if len(content) > MAX_FILE_SIZE:
            raise FileValidationError("文件超过大小上限")
        suffix = path.suffix.lower()
        if (
            content_type not in ALLOWED_FILE_TYPES
            or suffix not in ALLOWED_FILE_TYPES[content_type]
        ):
            raise FileValidationError("文件类型或扩展名不允许")
        return suffix
