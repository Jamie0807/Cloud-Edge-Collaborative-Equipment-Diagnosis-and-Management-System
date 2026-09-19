# 云端 API

当前垂直切片提供 Spring Boot 云端 API 的领域服务和 REST 接口：

- 接收边端状态，按云端接收时间执行超过 60 秒离线判断。
- 接收诊断事件，完整保留 `assetId`、`terminalId`、`edgeId`、`eventId`。
- 相同 `eventId` 的重复请求返回幂等结果；业务字段不一致时返回冲突错误。
- 支持资产、终端、边端、模态和 UTC 半开时间范围的组合查询。
- 空查询结果返回空集合，而不是错误。

## 接口

- `POST /api/v1/edge-statuses`
- `POST /api/v1/diagnostic-events`
- `GET /api/v1/diagnostic-events`
- `GET /api/v1/diagnostic-events/{eventId}`
- `GET /actuator/health`

当前切片使用内存仓储验证领域行为；PostgreSQL、Flyway 迁移、认证授权和审计持久化属于后续 T-005 增量，不能将当前内存实现视为生产持久化完成。

## 验证

```bash
mvn -q test
mvn -q spotless:check
<!-- cspell:disable-next-line -->
mvn -q -DskipTests package
```
