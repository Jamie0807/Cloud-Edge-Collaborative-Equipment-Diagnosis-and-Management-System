# ADR-001 云边诊断的存储、安全与可靠性基线

- **状态：** Accepted
- **日期：** 2026-09-18
- **关联规格：** [`../../specs/001-cloud-edge-diagnostics/spec.md`](../../specs/001-cloud-edge-diagnostics/spec.md)
- **关联计划：** [`../../specs/001-cloud-edge-diagnostics/plan.md`](../../specs/001-cloud-edge-diagnostics/plan.md)
- **决策来源：** 用户确认 D-006；用户授权对 D-007、D-008、D-011、D-012、D-013 采用调研后的推荐方案。

## 背景

系统需要在终端离线、云端暂不可用、证据文件较大或算法失败时保持可追溯性。数据库、证据访问、身份认证、重试和查询分页如果只停留在代码默认行为，会造成重复事件、越权下载、失效证据地址和不可恢复的积压。

## 决策

1. 云端使用 PostgreSQL 18 + Flyway；核心身份和关系使用独立列、外键和唯一约束，`eventId` 唯一。JSONB 只承载确有演进需求的扩展载荷。
2. 边端保留受控本地证据副本；云端使用 MinIO/S3 兼容对象存储，保存对象 key、SHA-256 和媒体元数据。Web 下载由云端按授权生成短时 presigned URL，不暴露边端路径或永久公开 URL。
3. 本地使用环境注入的独立服务令牌；生产使用 mTLS 或短期服务令牌；Web 使用 OIDC Authorization Code + PKCE，云端校验 JWT。凭据不得入库、入日志或进入 URL。
4. outbox 状态为 `PENDING/SENDING/RETRYABLE/FAILED/SENT`。网络错误、408、429、5xx 遵循有限指数退避、全抖动和 `Retry-After`；最多 10 次；明确 4xx 校验/鉴权错误不自动重试，但保留人工重放。
5. 文件校验失败在边端拒绝且不创建业务事件；算法失败创建可查询的 `FAILED` 事件，保留已验证证据和错误码，不伪造成功。
6. 查询采用服务端页码分页：默认 `page=1,size=20`，最大 `size=100`，按 `occurredAt DESC,eventId DESC` 稳定排序，过滤条件 AND 组合，默认最近 30 天，时间范围为 UTC `[from,to)`。

## 取舍

- PostgreSQL 相比 MySQL 提供更丰富的 JSONB、UUID、索引和约束能力，但仍保持 Spring Data JPA 的关系模型，避免把业务数据全部塞入 JSON。
- 对本期管理端，页码分页比游标分页更易理解和验证；通过页大小上限、稳定排序和复合索引控制风险。达到高吞吐或深分页容量阈值后，再以 ADR 评估游标/scroll API。
- presigned URL 仅是短期访问凭证，不等于对象永久公开；应用必须控制过期时间、权限、对象 key 和审计日志。

## 外部依据

- [PostgreSQL 18 官方介绍](https://www.postgresql.org/about/)
- [PostgreSQL 索引与排序](https://www.postgresql.org/docs/18/indexes-ordering.html)
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)
- [RFC 9110 HTTP 语义与 Retry-After](https://www.rfc-editor.org/rfc/rfc9110.html)
- [Amazon S3 presigned URL 文档](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html)
- [Spring Data JPA 分页与排序](https://docs.spring.io/spring-data/jpa/reference/repositories/core-concepts.html)

## 后续必须补齐

实现前仍需在容量与运行文档中明确单文件大小、事件吞吐、outbox 积压上限、证据保留/删除周期、备份恢复、RTO/RPO、密钥轮换和审计保留期；这些参数不能由本 ADR 的默认值替代。
