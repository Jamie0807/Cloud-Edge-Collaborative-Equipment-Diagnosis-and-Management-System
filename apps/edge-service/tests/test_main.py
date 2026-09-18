from edge_service.main import health


def test_health_reports_ready_status() -> None:
    assert health() == {"status": "ok", "service": "edge-service"}
