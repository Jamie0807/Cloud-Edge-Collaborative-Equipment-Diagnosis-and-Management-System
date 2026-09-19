"""边端接入边界的元数据标准化。"""

from collections.abc import Mapping

REQUIRED_IDENTIFIERS = ("assetId", "terminalId", "edgeId", "eventId")


def normalize_metadata(metadata: Mapping[str, object]) -> dict[str, str]:
    """保留四个独立标识，不混淆各自业务语义。"""
    normalized: dict[str, str] = {}
    for identifier in REQUIRED_IDENTIFIERS:
        value = metadata.get(identifier)
        if not isinstance(value, str) or not value:
            raise ValueError(f"{identifier} 字段必填")
        normalized[identifier] = value
    return normalized
