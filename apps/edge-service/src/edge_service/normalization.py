"""Metadata normalization for the edge-service boundary."""

from collections.abc import Mapping

REQUIRED_IDENTIFIERS = ("assetId", "terminalId", "edgeId", "eventId")


def normalize_metadata(metadata: Mapping[str, object]) -> dict[str, str]:
    """Return required identifiers without conflating their individual meanings."""
    normalized: dict[str, str] = {}
    for identifier in REQUIRED_IDENTIFIERS:
        value = metadata.get(identifier)
        if not isinstance(value, str) or not value:
            raise ValueError(f"{identifier} is required")
        normalized[identifier] = value
    return normalized
