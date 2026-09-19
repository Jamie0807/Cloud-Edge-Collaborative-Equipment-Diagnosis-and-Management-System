# 跨服务契约

契约版本 `0.1.0` 为云边诊断功能定义传输无关的 JSON Schema 2020-12 契约和轻量 TypeScript 校验器。服务应从 `src/identifiers.ts` 使用 `contractSchemas` 与 `validateContract`，不得复制载荷类型。

标识矩阵是有意设计的：

| 契约              | 必填标识                                     |
| ----------------- | -------------------------------------------- |
| 终端心跳          | `terminalId`、`edgeId`                       |
| 检测上传元数据    | `assetId`、`terminalId`、`edgeId`、`eventId` |
| 边端状态上报      | `edgeId`                                     |
| 诊断事件/查询响应 | 四个标识全部必填                             |

`assetId`、`terminalId`、`edgeId` 和 `eventId` 是相互独立的字段。不适用某个标识的消息应省略该字段；任何服务不得推导、拼接或改名来替代另一个标识。

传输时间必须是以 `Z` 结尾的 UTC ISO-8601 值。模态值为 `infrared`、`acoustic` 和 `partial_discharge`；置信度及资源利用率范围为 0 到 1。证据地址只能是受控 `s3://` 对象地址或授权的 HTTPS 地址，不能是客户端文件系统路径，也不能包含 URL 凭据。对象存储桶和域名白名单由部署环境配置，本契约不硬编码具体主机。

未知字段会被拒绝。诊断查询对已提供的筛选条件采用 AND 语义，时间范围使用 UTC `[from,to)`，默认页码为 1、页大小为 20，最大页大小为 100。空查询结果用 `items: []` 表示。

`eventId` 在事件创建时生成一次，并在重试中保持不变。云端契约区分 `ACCEPTED` 和 `DUPLICATE_ACCEPTED`；业务字段不同的重放请求返回 `CONFLICT` 和 `IDEMPOTENCY_CONFLICT`，不能创建新事件。
