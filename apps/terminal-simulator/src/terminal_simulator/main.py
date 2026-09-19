"""终端模拟器：按配置生成夹具文件，并通过边端地址发送数据。"""

from __future__ import annotations

import json
import logging
import secrets
import time
import urllib.error
import urllib.request
import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import Event
from typing import Literal, Protocol, cast
from urllib.parse import urlsplit

logger = logging.getLogger(__name__)
UTC = timezone.utc
Modality = Literal["infrared", "acoustic", "partial_discharge"]
ALLOWED_MODALITIES = frozenset({"infrared", "acoustic", "partial_discharge"})


def _validate_edge_url(edge_url: str) -> str:
    parsed = urlsplit(edge_url)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.netloc
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("边端地址必须是没有查询参数的 HTTP(S) 地址")
    return edge_url.rstrip("/")


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("时间必须带 UTC 时区")
    return value.astimezone(UTC)


def _isoformat(value: datetime) -> str:
    return _as_utc(value).isoformat().replace("+00:00", "Z")


def _new_uuid7() -> str:
    """生成不依赖第三方库的 UUIDv7 字符串。"""

    timestamp_ms = int(time.time() * 1000) & ((1 << 48) - 1)
    random_a = secrets.randbits(12)
    random_b = secrets.randbits(62)
    value = (
        (timestamp_ms << 80) | (0x7 << 76) | (random_a << 64) | (0b10 << 62) | random_b
    )
    return str(uuid.UUID(int=value))


@dataclass(frozen=True)
class TerminalConfig:
    terminal_id: str
    asset_id: str
    edge_id: str
    site: str
    modality: Modality
    collection_interval_seconds: int
    edge_url: str = "http://edge.local:8000"
    heartbeat_interval_seconds: int = 10

    def __post_init__(self) -> None:
        identifiers = {
            "terminalId": self.terminal_id,
            "assetId": self.asset_id,
            "edgeId": self.edge_id,
            "site": self.site,
        }
        if any(not value.strip() for value in identifiers.values()):
            raise ValueError("终端、资产、边端和站点标识不能为空")
        if self.modality not in ALLOWED_MODALITIES:
            raise ValueError("终端模态不在允许范围内")
        if (
            self.collection_interval_seconds <= 0
            or self.heartbeat_interval_seconds <= 0
        ):
            raise ValueError("采集和心跳周期必须是正整数")
        object.__setattr__(self, "edge_url", _validate_edge_url(self.edge_url))


@dataclass(frozen=True)
class DetectionEvent:
    event_id: str
    metadata: dict[str, object]
    file_path: Path


@dataclass(frozen=True)
class EdgeResponse:
    accepted: bool
    retryable: bool = False
    message: str = ""

    @classmethod
    def ok(cls) -> EdgeResponse:
        return cls(accepted=True)


class EdgeValidationError(ValueError):
    """边端明确拒绝的不可自动重试错误。"""


class EdgeClient(Protocol):
    def send_heartbeat(self, payload: Mapping[str, object]) -> EdgeResponse: ...

    def upload_detection(self, event: DetectionEvent) -> EdgeResponse: ...


class HttpEdgeClient:
    """使用已配置的边端地址发送 JSON 和 multipart 请求。"""

    def __init__(self, edge_url: str, timeout_seconds: float = 5.0) -> None:
        self.edge_url = _validate_edge_url(edge_url)
        self.timeout_seconds = timeout_seconds

    def send_heartbeat(self, payload: Mapping[str, object]) -> EdgeResponse:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        return self._post(
            f"{self.edge_url}/api/v1/terminal-heartbeats",
            body,
            {"Content-Type": "application/json", "Accept": "application/json"},
        )

    def upload_detection(self, event: DetectionEvent) -> EdgeResponse:
        boundary = f"----diagnostics-{secrets.token_hex(12)}"
        body = self._multipart_body(event, boundary)
        return self._post(
            f"{self.edge_url}/api/v1/detection-events",
            body,
            {
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "Accept": "application/json",
            },
        )

    def _post(self, url: str, body: bytes, headers: Mapping[str, str]) -> EdgeResponse:
        request = urllib.request.Request(
            url, data=body, headers=dict(headers), method="POST"
        )
        try:
            with urllib.request.urlopen(
                request, timeout=self.timeout_seconds
            ) as response:
                status = response.getcode()
                if 400 <= status < 500:
                    raise EdgeValidationError(f"边端校验失败，HTTP 状态码 {status}")
                if status >= 500:
                    return EdgeResponse(
                        False,
                        retryable=True,
                        message=f"边端暂不可用，HTTP 状态码 {status}",
                    )
                return EdgeResponse.ok()
        except urllib.error.HTTPError as error:
            if 400 <= error.code < 500:
                raise EdgeValidationError(
                    f"边端校验失败，HTTP 状态码 {error.code}"
                ) from error
            return EdgeResponse(
                False, retryable=True, message=f"边端暂不可用，HTTP 状态码 {error.code}"
            )

    @staticmethod
    def _multipart_body(event: DetectionEvent, boundary: str) -> bytes:
        delimiter = f"--{boundary}".encode("ascii")
        chunks: list[bytes] = []
        chunks.extend(
            [
                delimiter,
                b'Content-Disposition: form-data; name="metadata"',
                b"Content-Type: application/json",
                b"",
                json.dumps(event.metadata, ensure_ascii=False).encode("utf-8"),
            ]
        )
        file_content = event.file_path.read_bytes()
        content_type = str(event.metadata["contentType"])
        chunks.extend(
            [
                delimiter,
                (
                    'Content-Disposition: form-data; name="file"; '
                    f'filename="{event.file_path.name}"'
                ).encode(),
                f"Content-Type: {content_type}".encode("ascii"),
                b"",
                file_content,
                delimiter + b"--",
                b"",
            ]
        )
        return b"\r\n".join(chunks)


DEFAULT_TERMINAL_CONFIGS: tuple[TerminalConfig, ...] = (
    TerminalConfig(
        terminal_id="terminal-infrared-001",
        asset_id="asset-transformer-001",
        edge_id="edge-site-a-001",
        site="site-a",
        modality="infrared",
        collection_interval_seconds=5,
    ),
    TerminalConfig(
        terminal_id="terminal-acoustic-001",
        asset_id="asset-transformer-002",
        edge_id="edge-site-a-001",
        site="site-a",
        modality="acoustic",
        collection_interval_seconds=20,
    ),
    TerminalConfig(
        terminal_id="terminal-partial-discharge-001",
        asset_id="asset-transformer-003",
        edge_id="edge-site-a-001",
        site="site-a",
        modality="partial_discharge",
        collection_interval_seconds=60,
    ),
)


def _config_string(
    values: Mapping[str, object], key: str, default: str | None = None
) -> str:
    value = values.get(key, default)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"配置字段 {key} 必须是非空字符串")
    return value


def _config_int(values: Mapping[str, object], key: str) -> int:
    value = values.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"配置字段 {key} 必须是整数")
    return value


def load_terminal_configs(config_path: Path) -> tuple[TerminalConfig, ...]:
    try:
        document = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("终端配置文件不可读或不是有效 JSON") from error
    if not isinstance(document, dict) or not isinstance(
        document.get("terminals"), list
    ):
        raise TypeError("终端配置文件必须包含 terminals 数组")

    configs: list[TerminalConfig] = []
    for index, value in enumerate(document["terminals"]):
        if not isinstance(value, dict):
            raise TypeError(f"第 {index + 1} 个终端配置必须是对象")
        modality = _config_string(value, "modality")
        if modality not in ALLOWED_MODALITIES:
            raise ValueError(f"第 {index + 1} 个终端模态不在允许范围内")
        configs.append(
            TerminalConfig(
                terminal_id=_config_string(value, "terminalId"),
                asset_id=_config_string(value, "assetId"),
                edge_id=_config_string(value, "edgeId"),
                site=_config_string(value, "site"),
                modality=cast(Modality, modality),
                collection_interval_seconds=_config_int(
                    value, "collectionIntervalSeconds"
                ),
                edge_url=_config_string(value, "edgeUrl", "http://edge.local:8000"),
                heartbeat_interval_seconds=_config_int(
                    value, "heartbeatIntervalSeconds"
                ),
            )
        )
    if not configs:
        raise ValueError("终端配置至少需要一个终端")
    return tuple(configs)


class TerminalSimulator:
    def __init__(self, configs: tuple[TerminalConfig, ...], fixture_root: Path) -> None:
        if not configs:
            raise ValueError("至少需要一个终端配置")
        self.configs = configs
        self.fixture_root = fixture_root
        self._last_heartbeat: dict[str, datetime] = {}
        self._last_collection: dict[str, datetime] = {}
        self._pending_events: dict[str, DetectionEvent] = {}

    def create_event(
        self, config: TerminalConfig, captured_at: datetime
    ) -> DetectionEvent:
        captured_at = _as_utc(captured_at)
        event_id = _new_uuid7()
        directory = self.fixture_root / config.modality
        directory.mkdir(parents=True, exist_ok=True)
        filename = f"{config.modality}-{event_id}.json"
        file_path = directory / filename
        metadata: dict[str, object] = {
            "assetId": config.asset_id,
            "terminalId": config.terminal_id,
            "edgeId": config.edge_id,
            "eventId": event_id,
            "site": config.site,
            "modality": config.modality,
            "capturedAt": _isoformat(captured_at),
            "originalFilename": filename,
            "contentType": "application/json",
        }
        file_path.write_text(json.dumps(metadata, ensure_ascii=False), encoding="utf-8")
        return DetectionEvent(event_id=event_id, metadata=metadata, file_path=file_path)

    def run_once(self, now: datetime, client: EdgeClient | None = None) -> None:
        now = _as_utc(now)
        for config in self.configs:
            target = client or HttpEdgeClient(config.edge_url)
            self._send_due_heartbeat(config, now, target)
            pending = self._pending_events.get(config.terminal_id)
            if pending is None and self._is_due(
                self._last_collection.get(config.terminal_id),
                now,
                config.collection_interval_seconds,
            ):
                pending = self.create_event(config, now)
                self._pending_events[config.terminal_id] = pending
            if pending is not None:
                self._send_pending_event(config, pending, now, target)

    def run_forever(
        self,
        stop_event: Event,
        client: EdgeClient | None = None,
        poll_interval_seconds: float = 1.0,
    ) -> None:
        while not stop_event.is_set():
            self.run_once(datetime.now(UTC), client)
            stop_event.wait(poll_interval_seconds)

    def _send_due_heartbeat(
        self, config: TerminalConfig, now: datetime, client: EdgeClient
    ) -> None:
        if not self._is_due(
            self._last_heartbeat.get(config.terminal_id),
            now,
            config.heartbeat_interval_seconds,
        ):
            return
        payload = {
            "terminalId": config.terminal_id,
            "edgeId": config.edge_id,
            "modality": config.modality,
            "sentAt": _isoformat(now),
        }
        try:
            response = client.send_heartbeat(payload)
            if response.accepted:
                self._last_heartbeat[config.terminal_id] = now
            elif response.retryable:
                logger.warning(
                    "心跳发送待重试 terminalId=%s edgeId=%s",
                    config.terminal_id,
                    config.edge_id,
                )
        except (ConnectionError, TimeoutError, OSError) as error:
            logger.warning(
                "心跳发送失败 terminalId=%s edgeId=%s error=%s",
                config.terminal_id,
                config.edge_id,
                error,
            )
        except EdgeValidationError as error:
            logger.error(
                "心跳校验失败 terminalId=%s edgeId=%s error=%s",
                config.terminal_id,
                config.edge_id,
                error,
            )

    def _send_pending_event(
        self,
        config: TerminalConfig,
        event: DetectionEvent,
        now: datetime,
        client: EdgeClient,
    ) -> None:
        try:
            response = client.upload_detection(event)
            if response.accepted:
                self._pending_events.pop(config.terminal_id, None)
                self._last_collection[config.terminal_id] = now
            elif response.retryable:
                logger.warning(
                    "检测事件待重试 eventId=%s terminalId=%s edgeId=%s",
                    event.event_id,
                    config.terminal_id,
                    config.edge_id,
                )
            else:
                self._pending_events.pop(config.terminal_id, None)
                self._last_collection[config.terminal_id] = now
                logger.error(
                    "检测事件被边端拒绝 eventId=%s terminalId=%s error=%s",
                    event.event_id,
                    config.terminal_id,
                    response.message,
                )
        except EdgeValidationError as error:
            self._pending_events.pop(config.terminal_id, None)
            self._last_collection[config.terminal_id] = now
            logger.error(
                "检测事件校验失败且不重试 eventId=%s terminalId=%s error=%s",
                event.event_id,
                config.terminal_id,
                error,
            )
        except (ConnectionError, TimeoutError, OSError) as error:
            logger.warning(
                "检测事件发送失败待重试 eventId=%s terminalId=%s edgeId=%s error=%s",
                event.event_id,
                config.terminal_id,
                config.edge_id,
                error,
            )

    @staticmethod
    def _is_due(
        last_run: datetime | None, now: datetime, interval_seconds: int
    ) -> bool:
        return last_run is None or (now - last_run).total_seconds() >= interval_seconds


def health() -> dict[str, str]:
    return {"status": "ok", "service": "terminal-simulator"}


def main() -> None:
    print(json.dumps(health(), ensure_ascii=False))


if __name__ == "__main__":
    main()
