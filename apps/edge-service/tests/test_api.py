import json
from pathlib import Path

from fastapi.testclient import TestClient

from edge_service.api import create_app
from edge_service.service import EdgeService


def test_heartbeat_endpoint_returns_terminal_state(tmp_path: Path) -> None:
    client = TestClient(create_app(EdgeService(tmp_path)))

    response = client.post(
        "/api/v1/terminal-heartbeats",
        json={
            "terminalId": "terminal-1",
            "edgeId": "edge-1",
            "modality": "infrared",
            "sentAt": "2026-09-19T12:00:00Z",
        },
    )

    assert response.status_code == 200
    assert response.json()["terminalId"] == "terminal-1"


def test_detection_endpoint_saves_multipart_file_and_metadata(tmp_path: Path) -> None:
    client = TestClient(create_app(EdgeService(tmp_path)))
    metadata = {
        "assetId": "asset-1",
        "terminalId": "terminal-1",
        "edgeId": "edge-1",
        "eventId": "018f0f2b-7b00-7000-8000-000000000002",
        "site": "site-a",
        "modality": "infrared",
        "capturedAt": "2026-09-19T12:00:00Z",
    }

    response = client.post(
        "/api/v1/detection-events",
        data={"metadata": json.dumps(metadata)},
        files={"file": ("sample.json", b"{}", "application/json")},
    )

    assert response.status_code == 200
    assert response.json()["eventId"] == metadata["eventId"]


def test_detection_endpoint_rejects_invalid_file_without_event(tmp_path: Path) -> None:
    client = TestClient(create_app(EdgeService(tmp_path)))
    metadata = {
        "assetId": "asset-1",
        "terminalId": "terminal-1",
        "edgeId": "edge-1",
        "eventId": "018f0f2b-7b00-7000-8000-000000000003",
        "site": "site-a",
        "modality": "infrared",
        "capturedAt": "2026-09-19T12:00:00Z",
    }

    response = client.post(
        "/api/v1/detection-events",
        data={"metadata": json.dumps(metadata)},
        files={"file": ("../escape.json", b"{}", "application/json")},
    )

    assert response.status_code == 422
    assert not list(tmp_path.glob("*/payload.*"))
