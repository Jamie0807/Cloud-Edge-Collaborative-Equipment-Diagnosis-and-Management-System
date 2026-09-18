# 001 云边协同设备诊断管理计划

**状态：** Ready for implementation review — 业务编码尚未开始。
**关联规格：** [`spec.md`](spec.md)
**分析依据：** [`../../docs/requirements/001-cloud-edge-diagnostics-analysis.md`](../../docs/requirements/001-cloud-edge-diagnostics-analysis.md)

## 1. 计划目标和实施前置条件

计划依据已确认的分析文档 D-001 至 D-014，交付一个可本地运行、可部署、可测试和可观测的终端→边端→云端→Web 诊断主链路。当前工作树已具备 monorepo、质量入口和 Spec Kit 骨架，但业务行为尚未实现；本计划不替代已批准的 bootstrap 产物。

开始实现前必须确保以下事项有契约和测试：协议/确认语义、边端/云端/Web 技术落实、数据库迁移、认证边界、证据文件存储、`eventId` 幂等与重试策略，以及生产参数的版本边界。

## 2. 批准架构

```text
Python terminal-simulator
  - scheduled heartbeat / local fixture generation
  - terminal→edge HTTP multipart + JSON heartbeat
                  |
                  v
Python FastAPI edge-service
  - terminal registry / metadata validation / controlled file store
  - simulated analyzer / persistent outbox / retry worker
  - edge→cloud HTTPS REST (edge status + diagnosis)
                  |
                  v
Spring Boot cloud-api ── PostgreSQL 18 + Flyway
  - idempotent ingestion / relationship management / offline evaluation / query APIs
  - evidence URI metadata (MinIO/S3-compatible object store for local development)
                  |
                  v
Vue 3 + TypeScript web
  - edge list / diagnosis list+filters / diagnosis detail
```

推荐将服务职责固定如下：

| 单元                      | 责任                                                    | 禁止责任                                 |
| ------------------------- | ------------------------------------------------------- | ---------------------------------------- |
| `apps/terminal-simulator` | 配置、定时心跳、夹具文件生成、向边端上传                | 访问云端、算法、数据库持久化             |
| `apps/edge-service`       | 终端接入、文件保存、标准化、模拟算法、outbox、云端上报  | Web 展示、云端数据直接写入、真实模型承诺 |
| `apps/cloud-api`          | 关系/状态/诊断持久化、60 秒离线判断、幂等接收、查询 API | 直接读取边端磁盘、终端接入               |
| `apps/web`                | 管理端 API 调用、列表、筛选、详情与 UI 状态             | 直连 PostgreSQL、业务幂等判断            |
| `packages/contracts`      | 跨服务 schema、枚举、共享 fixture 约束                  | 运行时业务逻辑或服务私有实现             |

## 3. 批准数据计划

### 3.1 身份与关系模型

| 实体/记录                 | 建议字段                                                                                            | 关键约束                                               |
| ------------------------- | --------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| `assets`                  | `asset_id`、名称/站点等已确认管理字段                                                               | `asset_id` 是独立业务键；禁止通过 `terminal_id` 推导。 |
| `terminals`               | `terminal_id`、`edge_id`、`asset_id`、站点、模态、采集周期、`last_seen_at`、状态                    | 终端关系变更须验证目标资产/边端存在。                  |
| `edges`                   | `edge_id`、站点、`last_seen_at`、状态、最近资源指标                                                 | 状态由云端接收时间和 60 秒规则计算。                   |
| `edge_status_reports`     | `edge_id`、CPU、内存、GPU/NPU、`reported_at`、`received_at`                                         | 资源缺失表示 unavailable，不虚构数值。                 |
| `diagnostic_events`       | `event_id`、`asset_id`、`terminal_id`、`edge_id`、模态、发生时间、文件 URI/hash、分析字段、接收时间 | `event_id` 唯一；四个 ID 各自是持久化列和 API 字段。   |
| `edge_outbox`（边端本地） | `event_id`、规范化载荷、状态、重试次数、下次重试时间、最后错误                                      | 未得到云端成功确认不得删除；需要可重放。               |

建议云端使用 Flyway 管理顺序迁移，应用层验证 ID 关联，数据库用外键或等价完整性约束。PostgreSQL 18 是已确认方向；边端 outbox 使用 SQLite 或同一边端轻量持久化方案，不与云端数据库直连。存储/迁移脚本与任何数据库初始化均不在本次草案创建范围内。

### 3.2 时间与状态

- 所有 API 传输时间为 UTC ISO-8601，持久层采用时区安全类型或统一 UTC 约定。
- 终端心跳每 10 秒；采集默认红外 5 秒、声纹 20 秒、局放 60 秒，均能配置。
- 云端离线计算使用 `received_at`：`now - last_received_at > 60 seconds` 时对应 `edgeId` 离线。
- 边端状态推荐 10 秒上报，确保正常情况下可稳态满足云端阈值；该间隔不是题目既定值。
- 诊断事件发生时间、算法完成时间、云端接收时间不得混为同一字段。

### 3.3 文件与分析

终端上传的客户端文件名只作元数据；边端用 `eventId`/随机安全名映射到受控目录，验证扩展名、MIME（若可用）、大小、空文件与路径，持久化校验过的文件引用和 hash。算法只接收边端产生的路径；其结果包含 `defectType`、`confidence`、`severity` 和 `analyzedAt`，失败则返回明确错误分类，不制造成功诊断。

本地开发把证据副本放入 MinIO/S3 兼容对象存储，云端保存对象 key、SHA-256 和媒体元数据；详情接口按已认证用户权限生成短时 presigned GET URL。任何证据访问不得暴露边端路径或永久公开 URL。

## 4. 接口与契约计划

以下为实现阶段必须遵守的接口形状；具体错误码和认证头实现时必须与 D-001、D-002、D-008 及契约测试保持一致。

| 流向          | 推荐端点/消息                             | 最小请求字段                                                            | 成功与失败语义                                                 |
| ------------- | ----------------------------------------- | ----------------------------------------------------------------------- | -------------------------------------------------------------- |
| terminal→edge | `POST /api/v1/terminal-heartbeats`        | `terminalId`、`edgeId`、模态、`sentAt`                                  | 成功更新接收时间；未知/不匹配终端返回校验错误。                |
| terminal→edge | `POST /api/v1/detection-events` multipart | 文件 + `assetId`、`terminalId`、`edgeId`、`eventId`、模态、`capturedAt` | 仅校验成功后保存/入分析；非法文件/字段不创建事件。             |
| edge→cloud    | `POST /api/v1/edge-statuses`              | `edgeId`、站点、CPU、内存、GPU/NPU、`reportedAt`                        | 云端记录接收时间，返回接受确认。                               |
| edge→cloud    | `POST /api/v1/diagnostic-events`          | 四个 ID、模态、时间、分析字段、证据 URI/hash                            | 第一次返回创建/接受；相同 `eventId` 返回幂等接受，语义可区分。 |
| web→cloud     | `GET /api/v1/edges`                       | 可选状态/站点/分页                                                      | 返回 `edgeId`、站点、在线状态、最后在线时间。                  |
| web→cloud     | `GET /api/v1/diagnostic-events`           | `assetId`、`terminalId`、`edgeId`、模态、起止时间、分页                 | 合并已给条件筛选，结果始终含四个 ID。                          |
| web→cloud     | `GET /api/v1/diagnostic-events/{eventId}` | `eventId`                                                               | 返回完整诊断、证据文件地址和可用性错误。                       |

每份 schema 按消息类型约束适用标识：终端心跳必须有 `terminalId`、`edgeId`；边端状态必须有 `edgeId`；检测上传、诊断结果和查询响应必须有四个独立 ID。不适用字段不得伪造或拼接。所有 schema 还应约束模态枚举、置信度范围、严重等级枚举、UTC 时间、证据 URI，以及错误对象的机器码、消息和关联 ID（适用时）。契约测试也要覆盖未知字段处理、重复 `eventId` 和字段不一致重放策略。

## 5. 可靠性、安全与可观测性计划

- **幂等和重试：** `eventId` 由终端生成 UUIDv7；边端持久 outbox；云端 `event_id` 唯一约束；网络错误、408、429、5xx 可重试并遵守 `Retry-After`，指数退避+全抖动，最多 10 次；明确 4xx 校验/鉴权错误不自动重试，保留人工重放入口。
- **认证：** 本地使用环境注入的独立服务令牌；生产使用 mTLS 或短期服务令牌；Web 使用 OIDC Authorization Code + PKCE，云端校验 JWT。不可把凭据放入仓库、日志或 URL。
- **文件安全：** 受控根目录、随机存储名、大小/类型白名单、禁止客户端路径、错误时清理未提交临时文件。云端不挂载边端磁盘。
- **日志与度量：** 每个处理阶段记录 `eventId`、`assetId`、`terminalId`、`edgeId`（适用时）、操作和结果；屏蔽 token/文件内容。追踪 outbox 积压、失败数、最后成功上报时间。
- **降级：** 云端不可用不阻止边端保存/分析，但会使 outbox 增长；文件/算法无效不会创建“成功”诊断；对象存储不可用时保留边端受控证据和待处理状态，不生成带失效证据地址的成功事件。

## 6. Web 页面计划

| 页面         | 数据源                             | 必须显示/交互                                                                  | 状态                                       |
| ------------ | ---------------------------------- | ------------------------------------------------------------------------------ | ------------------------------------------ |
| 边端节点列表 | `GET /edges`                       | `edgeId`、站点、在线状态、最后在线时间                                         | 初始加载、空列表、API 错误、可选刷新。     |
| 诊断结果列表 | `GET /diagnostic-events`           | 资产、终端、边端、模态、缺陷、置信度、严重等级、发生时间；按资产/边端/模态筛选 | 首次加载、筛选加载、无结果、查询错误。     |
| 诊断详情     | `GET /diagnostic-events/{eventId}` | 四个 ID、全部诊断字段、证据文件地址                                            | 加载、未找到、API 错误、证据不可访问提示。 |

页面不直接连 PostgreSQL，也不在浏览器计算 60 秒离线规则；只展示云端计算的状态。证据访问由云端按 D-007/D-008 生成短时授权地址，并显示不可用/过期提示。

## 7. 测试与验收计划

| 层次              | 重点覆盖                                                              | 建议工具                                                  |
| ----------------- | --------------------------------------------------------------------- | --------------------------------------------------------- |
| 终端单元测试      | 周期配置、四个 ID 载荷、仅指向边端、文件夹具元数据                    | pytest + 可控时钟/HTTP mock                               |
| 边端单元/集成测试 | 心跳状态、元数据/文件拒绝、安全保存、算法成功/失败、outbox 状态和重试 | pytest + 临时目录/测试数据库                              |
| 契约测试          | 每条跨服务载荷的必填字段、ID 独立性、枚举、时间、幂等和错误响应       | schema tests in `packages/contracts`                      |
| 云端 JUnit        | 状态接收、60 秒离线边界、`eventId` 幂等、关系校验、多维查询、异常响应 | JUnit 5 + Spring Boot Test + Testcontainers（PostgreSQL） |
| Web 组件测试      | 列表字段、筛选请求、详情、加载/空/错误状态                            | Vitest + Vue Testing Library                              |
| 端到端            | 三种模态至少各一事件；终端→边端→云端→Web 可查询；云端短暂不可用后补报 | Playwright + 容器/本地服务编排                            |

| 验证项 | 覆盖需求                                 | 最低自动化证据                                            | 归属任务            |
| ------ | ---------------------------------------- | --------------------------------------------------------- | ------------------- |
| VT-001 | FR-001～FR-003、US-001                   | 终端周期、心跳、四 ID、仅向边端发送的 pytest              | T-003、T-007        |
| VT-002 | FR-002、FR-004～FR-006、FR-012、US-002   | 边端心跳、文件拒绝/安全保存、算法成功/失败、outbox pytest | T-004、T-007        |
| VT-003 | FR-003、FR-004、FR-006、NFR-002、NFR-004 | 跨服务 schema 的有效/无效/重放/错误响应契约测试           | T-002、T-007        |
| VT-004 | FR-006、FR-007、FR-009、NFR-005、US-003  | 云端不可用后 outbox 保留、恢复后同 `eventId` 重放集成测试 | T-004、T-005、T-007 |
| VT-005 | FR-007～FR-010、FR-012、US-003、US-004   | 状态接收、59/60/61 秒边界、幂等、关系/查询/错误 JUnit     | T-005、T-007        |
| VT-006 | FR-008、FR-010、FR-011、NFR-006、US-005  | Web 组件状态测试及查询到详情的 Playwright 链路            | T-006、T-007        |
| VT-007 | NFR-001、NFR-003、NFR-005～NFR-009       | 启动/配置、质量门禁、敏感信息、恢复和追踪性审查           | T-007、T-008        |

TDD 顺序固定为：先写针对上述验证项的失败测试（RED）→最小实现（GREEN）→只做必要重构→运行该层测试及契约测试→全量 `pnpm validate`。当前骨架的质量命令可运行，但本计划不把骨架健康测试误认为业务验收证据。

## 8. 实施顺序、风险与决策门

1. 确认 D-001 至 D-014，并将最终选择写入批准 spec/plan；如选项有持久影响，补 ADR。
2. 验证治理 bootstrap 已集成并提供 `pnpm validate`、服务目录和测试入口。
3. 先定义跨服务契约和夹具，再以 TDD 实现单一红外事件的终端→边端→云端流程。
4. 加入边端 outbox、云端幂等和离线判定，再复用配置支持声纹和局放。
5. 实现查询 API 和三个 Web 视图，最后做端到端演练、故障重试和交付文档。

关键风险为文件可访问性、ID 幂等、时间口径和空 worktree 下的基础工程依赖。这些风险不得由临时业务代码掩盖；未确认即停止在规划阶段并上报所需决策。
