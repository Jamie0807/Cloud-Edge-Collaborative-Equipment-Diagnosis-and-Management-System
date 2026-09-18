# 云边协同诊断系统：无业务行为架构骨架

## 状态与范围

本文描述当前 `0.0.0` monorepo 的职责边界、启动入口和后续扩展槽位。它不是业务 spec、实现批准或生产就绪声明；终端采集、文件上传、算法、outbox、云端诊断查询和 Web 业务视图均未实现。

本骨架只允许健康检查、静态页面挂载、标识字段示例和确定性测试夹具，避免在需求决策未确认前形成业务行为。

## 工作区职责与依赖方向

| 工作区                    | 当前骨架                              | 允许的未来职责                                | 禁止越界                       |
| ------------------------- | ------------------------------------- | --------------------------------------------- | ------------------------------ |
| `apps/web`                | Vue 3 根组件和静态健康状态            | 管理端页面、云端 API client、加载/空/错误状态 | 直连数据库或边端               |
| `apps/cloud-api`          | Spring Boot 启动类和 Actuator health  | 云端关系、状态、诊断持久化、查询和离线判断    | 读取边端磁盘或接收终端业务载荷 |
| `apps/edge-service`       | Python health 命令和纯元数据校验函数  | 终端接入、受控文件、分析、outbox 和云端适配器 | Web 展示、直接写云端数据库     |
| `apps/terminal-simulator` | Python health 命令                    | 配置、心跳、测试文件生成和边端传输适配器      | 访问云端、数据库或真实模型     |
| `packages/contracts`      | 四个标识字段的 JavaScript schema 示例 | 语言无关契约、版本兼容和 schema 测试          | 服务私有业务逻辑               |
| `packages/test-fixtures`  | 确定性的健康测试数据                  | 合法/非法/边界契约夹具                        | 真实生产文件或个人数据         |

未来允许的网络方向只有：终端 → 边端 → 云端，以及 Web → 云端。当前骨架没有这些业务连接；应用之间不得通过共享可写数据库、内部模块导入或文件系统共享绕过职责边界。

## 四个独立标识

| 字段         | 含义                           |
| ------------ | ------------------------------ |
| `assetId`    | 被监测的物理资产               |
| `terminalId` | 采集数据的感知终端             |
| `edgeId`     | 接收、分析和上报数据的边端节点 |
| `eventId`    | 一次检测/诊断事件的全链路标识  |

当前示例只表达字段存在，不决定生成方、唯一性范围、时间语义、幂等或协议版本。上述决策必须由 feature spec 和 ADR 明确后，才能进入契约实现。

## 当前入口与健康语义

| 组件               | 当前入口                                                                    | 验证含义                                                   |
| ------------------ | --------------------------------------------------------------------------- | ---------------------------------------------------------- |
| Web                | `pnpm --dir apps/web dev --host 127.0.0.1`                                  | 页面挂载并展示静态 `Health: checking`，不代表后端健康      |
| Edge               | `PYTHONPATH=apps/edge-service/src python3 -m edge_service.main`             | 输出 edge health JSON 后退出，不监听 HTTP                  |
| Terminal           | `PYTHONPATH=apps/terminal-simulator/src python3 -m terminal_simulator.main` | 输出 terminal health JSON 后退出，不产生业务文件           |
| Cloud              | `mvn -f apps/cloud-api/pom.xml spring-boot:run`                             | Actuator `/actuator/health` 返回 `UP`，不代表业务 API 可用 |
| Contracts/fixtures | 各自 workspace 的 Vitest 测试                                               | 校验示例和确定性测试数据，不启动服务                       |

云端健康检查绑定 Spring Boot Actuator；Python 入口是本地 health-only 命令；Web 健康文本是静态骨架。生产存活、就绪、依赖检查和认证边界须在批准的 feature 中分别定义。

## 后续扩展槽位

- Web：页面、API client、状态和错误展示；根组件保持装配职责。
- Cloud：HTTP 适配层 → 应用用例 → 领域模型 → 持久化适配层；领域层不得反向依赖 HTTP 或数据库实现。
- Edge：接入适配层 → 应用流程 → 文件存储/分析/outbox 适配器；容量、恢复和安全协议先于实现。
- Terminal：场景输入 → 调度流程 → 边端传输适配器；目标地址只能来自边端配置。
- Contracts：语言无关 schema、版本说明、兼容性测试；不携带应用内部对象或密钥。
- Fixtures：合法、非法、边界和版本兼容样例；数据必须确定、可审查且不含真实生产内容。

建立任一业务模块前，必须完成 `Constitution → Specify → Clarify → Plan → Tasks → Implement → Verify/Analyze`，并保持 `spec → plan → tasks → files → tests` 追踪。长期选型记录在 ADR 中。

## 生产准入条件

`0.0.0` 骨架不具备生产就绪性。业务实现前必须在需求和 ADR 中明确：

- 可用性、容量、文件大小、并发规模、限流和超限行为；
- 超时、重试、幂等、断网恢复、崩溃恢复、备份、RTO/RPO；
- 终端/边端/Web 的认证授权、TLS、证据访问、路径安全和密钥管理；
- 结构化日志、指标、追踪、告警、审计事件和脱敏规则；
- 数据库迁移/回滚、契约兼容窗口、部署拓扑和数据生命周期。

## 验证入口

`pnpm validate` 是项目唯一全量质量入口，覆盖 lint、format、spellcheck、typecheck、Vitest、pytest、JUnit、Playwright 和 build。局部命令只能定位问题，不能替代全量结论。当前骨架门禁通过只证明工程基线可运行，不证明业务验收已经完成。
