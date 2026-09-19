# 终端模拟器

终端模拟器只访问配置的边端地址，不包含任何云端客户端。它提供三种可配置终端：红外、声纹和局放。

## 运行约束

- 每台终端默认每 10 秒发送一次 JSON 心跳。
- 红外、声纹、局放默认分别每 5、20、60 秒生成检测文件和元数据。
- 每个事件在采集时生成 UUIDv7 形式的 `eventId`，直到边端确认接收前保持不变。
- 检测元数据独立保留 `assetId`、`terminalId`、`edgeId`、`eventId`，时间使用 UTC ISO-8601。
- 网络错误、超时和边端暂不可用响应会保留事件并记录可观察日志；校验错误不会自动重试。

## 配置

默认配置位于 `config/default.json`，可通过 `load_terminal_configs` 加载。边端地址必须是没有查询参数的 HTTP(S) 地址；配置不包含凭据。

核心调度入口是 `TerminalSimulator.run_once`，生产运行可使用 `run_forever` 配合停止事件。HTTP 实现使用 JSON 心跳和 multipart 检测上传：

- `POST /api/v1/terminal-heartbeats`
- `POST /api/v1/detection-events`

## 本地验证

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest -q
.venv/bin/ruff check src tests
.venv/bin/ruff format --check src tests
.venv/bin/mypy src
```
