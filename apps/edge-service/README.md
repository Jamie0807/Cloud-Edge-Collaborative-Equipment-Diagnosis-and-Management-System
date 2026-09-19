# 边端服务

边端服务负责终端心跳接入、检测文件安全保存、元数据标准化、模拟分析和本地 SQLite outbox。它不直接让终端访问云端；云端上报客户端将在后续任务中接入。

## 当前能力

- `POST /api/v1/terminal-heartbeats`：接收 JSON 心跳并记录终端最后在线时间。
- `POST /api/v1/detection-events`：接收 multipart 文件和 JSON 元数据。
- 独立保留 `assetId`、`terminalId`、`edgeId`、`eventId`。
- 使用事件 ID 目录和固定文件名保存文件，拒绝路径穿越、类型不匹配和超大文件。
- 模拟分析成功写入 `PENDING` outbox；空文件写入 `FAILED`，不伪造成功诊断。
- SQLite outbox 保留同一 `eventId`，网络错误可重试，云端校验错误不自动重试。

## 本地运行

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
# cspell:disable-next-line
PYTHONPATH=src .venv/bin/uvicorn edge_service.api:app --reload --port 8001
```

默认受控文件和 outbox 位于 `/tmp/diagnostics-edge-service`，可通过 `EDGE_STORAGE_ROOT` 修改。生产环境应使用环境变量注入服务身份和受控存储路径，不把凭据写入配置或日志。

## 本地验证

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q
.venv/bin/ruff check src tests
.venv/bin/ruff format --check src tests
.venv/bin/mypy src
```
