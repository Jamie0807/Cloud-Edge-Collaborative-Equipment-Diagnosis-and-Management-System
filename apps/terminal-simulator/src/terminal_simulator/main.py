"""Executable health-only entry point for the terminal simulator skeleton."""

import json


def health() -> dict[str, str]:
    return {"status": "ok", "service": "terminal-simulator"}


def main() -> None:
    print(json.dumps(health()))


if __name__ == "__main__":
    main()
