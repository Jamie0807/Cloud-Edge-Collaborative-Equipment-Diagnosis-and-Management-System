from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from edge_service.service import (
    CloudResponse,
    CloudValidationError,
    EdgeService,
    FileValidationError,
    OutboxStatus,
)

UTC = timezone.utc
METADATA = {
    "assetId": "asset-1",
    "terminalId": "terminal-1",
    "edgeId": "edge-1",
    "eventId": "018f0f2b-7b00-7000-8000-000000000001",
    "site": "site-a",
    "modality": "infrared",
    "capturedAt": "2026-09-19T12:00:00Z",
}


class FakeCloudClient:
    def __init__(self, outcomes: list[object]) -> None:
        self.outcomes = list(outcomes)
        self.payloads: list[dict[str, object]] = []

    def send_diagnostic(self, payload: dict[str, object]) -> CloudResponse:
        self.payloads.append(payload)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


def test_heartbeat_records_terminal_state() -> None:
    service = EdgeService(Path("/tmp/diagnostics-edge-test"))
    received_at = datetime(2026, 9, 19, 12, 0, tzinfo=UTC)

    result = service.receive_heartbeat(
        {
            "terminalId": "terminal-1",
            "edgeId": "edge-1",
            "modality": "infrared",
            "sentAt": "2026-09-19T11:59:59Z",
        },
        received_at,
    )

    assert result["terminalId"] == "terminal-1"
    assert result["edgeId"] == "edge-1"
    assert result["lastSeenAt"] == "2026-09-19T12:00:00Z"


def test_detection_is_saved_with_controlled_name_and_queued(tmp_path: Path) -> None:
    service = EdgeService(tmp_path)

    result = service.receive_detection(
        METADATA, "client-name.json", "application/json", b"{}"
    )

    assert result["eventId"] == METADATA["eventId"]
    assert result["assetId"] == METADATA["assetId"]
    assert result["terminalId"] == METADATA["terminalId"]
    assert result["edgeId"] == METADATA["edgeId"]
    saved_path = Path(str(result["storedPath"]))
    assert saved_path.parent == tmp_path / METADATA["eventId"]
    assert saved_path.name == "payload.json"
    assert saved_path.read_bytes() == b"{}"
    assert service.outbox_status(METADATA["eventId"]) == OutboxStatus.PENDING


@pytest.mark.parametrize(
    ("filename", "content_type"),
    [
        ("../escape.json", "application/json"),
        ("payload.exe", "application/octet-stream"),
    ],
)
def test_detection_rejects_unsafe_file_before_saving(
    tmp_path: Path, filename: str, content_type: str
) -> None:
    service = EdgeService(tmp_path)

    with pytest.raises(FileValidationError):
        service.receive_detection(METADATA, filename, content_type, b"payload")

    assert not any(path.is_dir() for path in tmp_path.iterdir())


def test_detection_rejects_invalid_time_and_modality(tmp_path: Path) -> None:
    service = EdgeService(tmp_path)

    with pytest.raises(ValueError, match="模态"):
        service.receive_detection(
            {**METADATA, "modality": "ultrasonic_video"},
            "payload.json",
            "application/json",
            b"{}",
        )
    with pytest.raises(ValueError, match="UTC"):
        service.receive_detection(
            {**METADATA, "capturedAt": "2026-09-19T12:00:00"},
            "payload.json",
            "application/json",
            b"{}",
        )


def test_algorithm_failure_is_recorded_without_success_result(tmp_path: Path) -> None:
    service = EdgeService(tmp_path)

    result = service.receive_detection(
        METADATA, "payload.json", "application/json", b""
    )

    assert result["status"] == "FAILED"
    assert result["errorCode"] == "EMPTY_FILE"
    assert service.outbox_status(METADATA["eventId"]) == OutboxStatus.FAILED


def test_outbox_retries_same_event_after_cloud_unavailable(tmp_path: Path) -> None:
    service = EdgeService(tmp_path)
    service.receive_detection(METADATA, "payload.json", "application/json", b"{}")
    client = FakeCloudClient([ConnectionError("云端暂不可达"), CloudResponse.ok()])
    first_attempt = datetime(2026, 9, 19, 12, 0, tzinfo=UTC)

    service.flush_outbox(client, first_attempt)
    assert service.outbox_status(METADATA["eventId"]) == OutboxStatus.RETRYABLE
    service.flush_outbox(client, first_attempt + timedelta(seconds=30))

    assert service.outbox_status(METADATA["eventId"]) == OutboxStatus.SENT
    assert [payload["eventId"] for payload in client.payloads] == [
        METADATA["eventId"]
    ] * 2


def test_cloud_validation_error_is_not_retried(tmp_path: Path) -> None:
    service = EdgeService(tmp_path)
    service.receive_detection(METADATA, "payload.json", "application/json", b"{}")
    client = FakeCloudClient([CloudValidationError("幂等冲突")])

    service.flush_outbox(client, datetime(2026, 9, 19, 12, 0, tzinfo=UTC))
    service.flush_outbox(client, datetime(2026, 9, 19, 12, 1, tzinfo=UTC))

    assert service.outbox_status(METADATA["eventId"]) == OutboxStatus.FAILED
    assert len(client.payloads) == 1
