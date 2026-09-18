import pytest

from edge_service.normalization import normalize_metadata


def test_normalize_metadata_preserves_each_identifier() -> None:
    metadata = normalize_metadata(
        {
            "assetId": "asset-1",
            "terminalId": "terminal-1",
            "edgeId": "edge-1",
            "eventId": "event-1",
        }
    )

    assert metadata == {
        "assetId": "asset-1",
        "terminalId": "terminal-1",
        "edgeId": "edge-1",
        "eventId": "event-1",
    }


@pytest.mark.parametrize("missing_key", ["assetId", "terminalId", "edgeId", "eventId"])
def test_normalize_metadata_rejects_missing_identifier(missing_key: str) -> None:
    payload = {
        "assetId": "asset-1",
        "terminalId": "terminal-1",
        "edgeId": "edge-1",
        "eventId": "event-1",
    }
    del payload[missing_key]

    with pytest.raises(ValueError, match=missing_key):
        normalize_metadata(payload)
