from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from terminal_simulator.main import (
    DEFAULT_TERMINAL_CONFIGS,
    EdgeResponse,
    EdgeValidationError,
    HttpEdgeClient,
    TerminalConfig,
    TerminalSimulator,
    health,
    load_terminal_configs,
)

UTC = timezone.utc


class FakeEdgeClient:
    def __init__(self, upload_results: list[object] | None = None) -> None:
        self.heartbeats: list[dict[str, object]] = []
        self.events: list[object] = []
        self.upload_results = list(upload_results or [])

    def send_heartbeat(self, payload: dict[str, object]) -> EdgeResponse:
        self.heartbeats.append(payload)
        return EdgeResponse.ok()

    def upload_detection(self, event: object) -> EdgeResponse:
        self.events.append(event)
        result = (
            self.upload_results.pop(0) if self.upload_results else EdgeResponse.ok()
        )
        if isinstance(result, BaseException):
            raise result
        return result


def test_health_reports_ready_status() -> None:
    assert health() == {"status": "ok", "service": "terminal-simulator"}


def test_default_configs_cover_three_modalities_and_periods() -> None:
    periods = {
        config.modality: config.collection_interval_seconds
        for config in DEFAULT_TERMINAL_CONFIGS
    }
    assert periods == {"infrared": 5, "acoustic": 20, "partial_discharge": 60}
    assert {
        config.heartbeat_interval_seconds for config in DEFAULT_TERMINAL_CONFIGS
    } == {10}
    assert {config.edge_url for config in DEFAULT_TERMINAL_CONFIGS} == {
        "http://edge.local:8000"
    }


def test_terminal_configs_can_be_loaded_from_json(tmp_path: Path) -> None:
    config_path = tmp_path / "terminals.json"
    config_path.write_text(
        '{"terminals":[{"terminalId":"t-1","assetId":"a-1","edgeId":"e-1",'
        '"site":"site-a","modality":"infrared","collectionIntervalSeconds":5,'
        '"heartbeatIntervalSeconds":10,"edgeUrl":"http://edge.local:8000"}]}',
        encoding="utf-8",
    )

    configs = load_terminal_configs(config_path)

    assert configs[0].terminal_id == "t-1"
    assert configs[0].collection_interval_seconds == 5


def test_run_once_sends_heartbeat_and_due_events_with_four_ids(tmp_path: Path) -> None:
    simulator = TerminalSimulator(DEFAULT_TERMINAL_CONFIGS, fixture_root=tmp_path)
    client = FakeEdgeClient()
    now = datetime(2026, 9, 19, 12, 0, tzinfo=UTC)

    simulator.run_once(now, client)

    assert len(client.heartbeats) == 3
    assert len(client.events) == 3
    for event in client.events:
        metadata = event.metadata  # type: ignore[attr-defined]
        assert {
            "assetId",
            "terminalId",
            "edgeId",
            "eventId",
            "site",
            "modality",
            "capturedAt",
            "originalFilename",
            "contentType",
        } <= metadata.keys()
        assert metadata["assetId"] != metadata["terminalId"]
        assert metadata["terminalId"] != metadata["edgeId"]
        assert metadata["eventId"]
        assert event.file_path.exists()  # type: ignore[attr-defined]


def test_collection_schedule_uses_five_twenty_and_sixty_seconds(tmp_path: Path) -> None:
    simulator = TerminalSimulator(DEFAULT_TERMINAL_CONFIGS, fixture_root=tmp_path)
    client = FakeEdgeClient()
    start = datetime(2026, 9, 19, 12, 0, tzinfo=UTC)

    for seconds in range(0, 61, 5):
        simulator.run_once(start + timedelta(seconds=seconds), client)

    counts = {
        modality: sum(event.metadata["modality"] == modality for event in client.events)  # type: ignore[attr-defined]
        for modality in ("infrared", "acoustic", "partial_discharge")
    }
    assert counts == {"infrared": 13, "acoustic": 4, "partial_discharge": 2}


def test_event_id_is_reused_until_edge_accepts(tmp_path: Path) -> None:
    simulator = TerminalSimulator(DEFAULT_TERMINAL_CONFIGS[:1], fixture_root=tmp_path)
    client = FakeEdgeClient([ConnectionError("边端暂不可达"), EdgeResponse.ok()])
    start = datetime(2026, 9, 19, 12, 0, tzinfo=UTC)

    simulator.run_once(start, client)
    simulator.run_once(start + timedelta(seconds=1), client)

    assert len(client.events) == 2
    assert client.events[0].event_id == client.events[1].event_id  # type: ignore[attr-defined]


def test_validation_error_is_logged_and_not_retried(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,  # cspell:disable-line
) -> None:
    simulator = TerminalSimulator(DEFAULT_TERMINAL_CONFIGS[:1], fixture_root=tmp_path)
    client = FakeEdgeClient([EdgeValidationError("元数据校验失败")])
    start = datetime(2026, 9, 19, 12, 0, tzinfo=UTC)

    simulator.run_once(start, client)
    simulator.run_once(start + timedelta(seconds=1), client)

    assert len(client.events) == 1
    assert "校验" in caplog.text  # cspell:disable-line


def test_http_client_only_builds_edge_requests(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    requests: list[object] = []

    class Response:
        def __enter__(self) -> object:
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def read(self) -> bytes:
            return b'{"accepted":true}'

        def getcode(self) -> int:
            return 200

    def fake_urlopen(request: object, timeout: float) -> Response:
        del timeout
        requests.append(request)
        return Response()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    client = HttpEdgeClient("http://edge.local:8000")
    config = DEFAULT_TERMINAL_CONFIGS[0]
    simulator = TerminalSimulator([config], fixture_root=tmp_path)
    event = simulator.create_event(config, datetime(2026, 9, 19, 12, 0, tzinfo=UTC))

    client.send_heartbeat(
        {
            "terminalId": config.terminal_id,
            "edgeId": config.edge_id,
            "modality": config.modality,
            "sentAt": "2026-09-19T12:00:00Z",
        }
    )
    client.upload_detection(event)

    assert [request.full_url for request in requests] == [  # type: ignore[attr-defined]
        "http://edge.local:8000/api/v1/terminal-heartbeats",
        "http://edge.local:8000/api/v1/detection-events",
    ]


def test_terminal_config_rejects_invalid_edge_url() -> None:
    with pytest.raises(ValueError, match="边端地址"):
        TerminalConfig(
            terminal_id="terminal-1",
            asset_id="asset-1",
            edge_id="edge-1",
            site="site-a",
            modality="infrared",
            collection_interval_seconds=5,
            edge_url="file:///tmp/edge",
        )
