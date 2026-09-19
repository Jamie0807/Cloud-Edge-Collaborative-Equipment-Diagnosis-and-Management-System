# 共享测试夹具

本包提供用于跨服务测试的确定性、非生产数据。

`src/index.ts` 和 `src/diagnostic.ts` 导出：

- `validDiagnosticEvents`：红外、声纹和局放事件；每个事件都保留独立的 `assetId`、`terminalId`、`edgeId` 和 UUIDv7 形式的 `eventId`。
- `invalidDiagnosticFixtures`：缺少标识、非法模态和非法 UTC 时间案例。
- `boundaryDiagnosticFixtures`：置信度 0、置信度 1 和最小文件大小边界案例。
- `duplicateDiagnosticEvents`：载荷和 `eventId` 完全相同的重放事件对。
- `safeFileMetadata`：只包含元数据，不引用或携带真实文件。

所有事件时间都是有效的 UTC ISO-8601 字符串，证据地址使用不含凭据的 `s3://` 形式。生产单文件最大大小尚未在需求中冻结，本包只表达契约已确定的最小正数边界。

包名入口为 `@diagnostics/test-fixtures`，健康夹具也可通过 `@diagnostics/test-fixtures/health` 引用。
