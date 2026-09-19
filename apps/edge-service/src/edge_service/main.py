"""边端服务的健康检查入口。"""

import json


def health() -> dict[str, str]:
    return {"status": "ok", "service": "edge-service"}


def main() -> None:
    print(json.dumps(health()))


if __name__ == "__main__":
    main()
