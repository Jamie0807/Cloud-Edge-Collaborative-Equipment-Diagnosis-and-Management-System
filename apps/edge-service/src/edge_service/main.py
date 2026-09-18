"""Executable health-only entry point for the edge service skeleton."""

import json


def health() -> dict[str, str]:
    return {"status": "ok", "service": "edge-service"}


def main() -> None:
    print(json.dumps(health()))


if __name__ == "__main__":
    main()
