from terminal_simulator.main import health


def test_health_reports_ready_status() -> None:
    assert health() == {"status": "ok", "service": "terminal-simulator"}
