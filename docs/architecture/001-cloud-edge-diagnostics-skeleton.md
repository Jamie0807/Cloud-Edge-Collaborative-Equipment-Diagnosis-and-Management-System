# 云边协同诊断系统：无业务架构骨架

## 状态与适用范围

本文描述当前工作区可观察到的结构，并为后续已批准的 feature 预留边界；不是业务 spec、实现计划或生产上线批准。当前版本为 `0.0.0` 骨架，尚未实现可运行的跨服务诊断主链路。

本次只新增本文，不修改源码、应用 README、业务 spec/plan/tasks、治理文件或质量配置。现有应用入口已足以表达最小结构，因此不新增空目录、无消费者的抽象类或伪业务接口。

检查时此隔离工作区缺少根 `README.md`、`AGENTS.md` 和 `docs/architecture/README.md`，也未提供任务引用的 spec/plan/tasks。本文依据本次任务及其提供的项目协议、六个工作区 README、源码、测试与脚本编写。缺失文档需由对应维护线后续核对；本文不替代其审批或约束。

## 职责与依赖方向

下表中的“目标职责”均为未来职责，不代表已实现。

| 工作区                    | 当前结构                                | 目标职责与边界                                                                 |
| ------------------------- | --------------------------------------- | ------------------------------------------------------------------------------ |
| `apps/web`                | Vue 3 根组件与静态健康文本              | 管理端仅通过云端 API 访问业务数据，不直连数据库或边端                          |
| `apps/cloud-api`          | Spring Boot 启动类、Actuator 健康端点   | 云端持久化、查询和管理接口；不得读取边端数据库                                 |
| `apps/edge-service`       | Python 本地健康命令、独立元数据校验函数 | 终端接入、文件保存、元数据标准化、模拟分析及待上报缓存；只通过明确契约访问云端 |
| `apps/terminal-simulator` | Python 本地健康命令                     | 模拟感知终端，只访问边端，不访问云端                                           |
| `packages/contracts`      | JavaScript 导出的标识字段 schema 示例   | 跨服务协议与兼容性约束，不依赖任一应用实现                                     |
| `packages/test-fixtures`  | 确定性的健康测试数据                    | 仅供测试使用的合成数据，不作为生产默认数据或运行时依赖                         |

未来允许的网络方向为：终端 → 边端 → 云端，以及 Web → 云端。当前这些业务连接均未建立；Python 入口无监听端口，也不发出网络请求。健康观测由本地命令或监控调用对应服务，不构成终端绕过边端的业务路径。

应用间通过契约通信，禁止跨应用导入内部模块、共享可写数据库或以文件系统共享绕过服务所有权。当前应用 manifest 未声明对两个共享包的消费关系。未来使用契约时应显式声明依赖；Python/Java 不能直接消费 JavaScript 模块，应在契约 feature 中确定语言无关格式、版本及生成或校验方式。

### 四种标识必须独立

| 字段         | 含义               | 不能替代的对象 |
| ------------ | ------------------ | -------------- |
| `assetId`    | 被诊断的物理资产   | 感知终端       |
| `terminalId` | 感知终端           | 资产或接收边端 |
| `edgeId`     | 接收数据的边端     | 终端或云端     |
| `eventId`    | 一次诊断事件的标识 | 任一设备标识   |

字段名和语义须贯穿未来契约、存储和测试；不可合并为含义不明的设备 ID。当前示例只声明四个必需字符串字段，不包含生成规则、唯一性范围、关联基数、时间语义、幂等或协议版本保证。这些规则必须由后续 feature 确定，不能从示例值推断。

## 当前入口与健康语义

以下命令均从 monorepo 工作区根目录执行。前置工具为 manifest 指定的 pnpm 10、兼容已安装前端依赖的 Node.js、Python 3.9 及以上；云端还需 Java 17 及以上和 Maven。Python 测试需要 pytest，格式检查需要 Ruff。依赖安装可能需要网络授权，本文不要求执行安装。当前没有统一启动脚本、Maven wrapper 或容器编排。

| 组件                 | 启动命令                                                                                               | 检查方式与实际含义                                                                                                    |
| -------------------- | ------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------- |
| Web                  | `pnpm --dir apps/web dev --host 127.0.0.1`                                                             | 打开 Vite 实际输出的地址，默认端口 5173；应显示标题及 `Health: checking`，仅证明页面挂载，不证明后端健康              |
| Edge                 | `PYTHONPATH=apps/edge-service/src python3 -m edge_service.main`                                        | 标准输出为 `{"status": "ok", "service": "edge-service"}`，随后退出；没有 HTTP 健康路由                                |
| Terminal             | `PYTHONPATH=apps/terminal-simulator/src python3 -m terminal_simulator.main`                            | 标准输出为 `{"status": "ok", "service": "terminal-simulator"}`，随后退出；没有 HTTP 健康路由                          |
| Cloud                | `mvn -f apps/cloud-api/pom.xml spring-boot:run -Dspring-boot.run.arguments=--server.address=127.0.0.1` | 默认端口 8080；另一个终端执行 `curl --fail http://127.0.0.1:8080/actuator/health`，预期 HTTP 200 与 `{"status":"UP"}` |
| Contracts / Fixtures | 无服务启动入口                                                                                         | 通过包测试检查示例，不监听端口                                                                                        |

Web 的 `src/main.js` 挂载 `src/App.vue`；Cloud 的 `CloudApiApplication.java` 启动应用，`application.yaml` 只显式暴露 health 管理端点。Python 的两个 `main.py` 调用本地 `health()`；`pyproject.toml` 还声明了安装后的命令入口，但上表直接使用源码模块，无需假设包已安装。

这些检查不包含数据库、存储、云边连接或业务就绪性检查。即使健康返回成功，也不能判定系统可接收诊断事件。当前未配置认证授权或生产部署防护，健康骨架仅适用于受控开发环境；上表将两个开发服务器绑定到回环地址。

### 已有独立代码的边界

边端 `src/edge_service/normalization.py` 的 `normalize_metadata` 检查四个字段是否为非空字符串并返回这些字段；其他字段被舍弃，纯空白字符串尚不会被拒绝。该函数未由健康入口调用，没有文件、网络或持久化行为。现有测试覆盖字段保留和缺失字段，但未覆盖所有类型与空值情况。本文如实记录该已有代码，不修改它，也不将它视为完整的元数据处理功能。

## 未来扩展槽位

下列是职责放置建议，尚未建立的路径不应被文档引用为可用模块。只有已批准 feature 才能建立代码与依赖，避免提前绑定框架或存储选型。

| 工作区    | 后续可引入的内部边界                                 | 进入实现前的约束                                           |
| --------- | ---------------------------------------------------- | ---------------------------------------------------------- |
| Web       | 页面、API 客户端、状态及错误展示                     | 先批准云端接口及加载、空、错误状态验收；根组件保持装配职责 |
| Cloud     | HTTP 适配层、应用用例、领域模型、持久化适配层        | 领域层不反向依赖 HTTP 或数据库实现；事务和权限边界需明确   |
| Edge      | 接入适配层、应用流程、文件存储、分析接口、上报适配层 | 接入、存储、算法及缓存分别有所有者；容量和恢复协议须先明确 |
| Terminal  | 场景输入、模拟器流程、边端传输适配层                 | 目标只能是边端；输入和发送策略须有独立验收                 |
| Contracts | 语言无关 schema、版本说明、兼容性测试                | 同时验证生产者与消费者；不携带应用内部对象或密钥           |
| Fixtures  | 合法、非法、边界与版本兼容样例                       | 数据确定、可追溯到契约、无真实生产文件或个人数据           |

终端采集、上传、算法、待上报缓存、云端诊断、查询与 Web 业务均未由本文实现。未来各功能仍须完成 Constitution → Specify → Clarify → Plan → Tasks → Implement → Verify/Analyze，建立 spec → plan → tasks → files → tests 追踪；长期选型应另立 ADR。本文不新增业务 API、事件结构或数据库设计。

## 生产准入与后续决策

`0.0.0` 不具备生产就绪性。本次范围仅接受本地骨架验证，不能理解为用户已接受生产风险。下列事项在对应能力进入实现或部署前必须由需求和 ADR 明确，具体指标、版本和风险接受人尚未获得批准；不得默认为延期豁免。

| 主题               | 必须明确的决策与验收                                                   |
| ------------------ | ---------------------------------------------------------------------- |
| 可用性、容量与性能 | 服务目标、文件大小及并发上限、边端磁盘预算、背压、限流、压测条件       |
| 恢复与一致性       | 超时、重试、幂等、断网恢复、进程崩溃后的数据归属与恢复验证             |
| 认证授权与证据安全 | 终端和边端身份、租户或资产访问控制、上传校验、路径安全、传输与存储保护 |
| 审计与可观测性     | 审计事件、关联标识、脱敏日志、指标、告警及存活和就绪检查的区别         |
| 迁移与回滚         | 契约兼容窗口、数据库迁移、部署回滚以及数据无法逆转时的恢复策略         |
| 数据生命周期       | 文件和元数据保留期限、清理一致性、备份恢复和删除权限                   |

## 验证入口与证据范围

`pnpm validate` 是现有唯一全量入口，依次执行 lint、格式、拼写、类型、单元测试、端到端测试与构建；失败后不应声称后续门禁已执行。单独运行门禁用于定位和提供局部证据，不替代全量通过。

| 命令                                                                                  | 覆盖范围                                 |
| ------------------------------------------------------------------------------------- | ---------------------------------------- |
| `pnpm exec prettier --check docs/architecture/001-cloud-edge-diagnostics-skeleton.md` | 本文格式                                 |
| `pnpm exec cspell docs/architecture/001-cloud-edge-diagnostics-skeleton.md`           | 本文英文拼写；不能验证中文语义           |
| `pnpm --dir apps/web test`                                                            | Vue 根组件标题及静态文本                 |
| `pnpm --dir packages/contracts test`                                                  | 示例的四个属性键；不等于完整 schema 验证 |
| `pnpm --dir packages/test-fixtures test`                                              | 健康样例确定性                           |
| `pnpm --dir apps/edge-service test`                                                   | 健康函数及已有标识校验                   |
| `pnpm --dir apps/terminal-simulator test`                                             | 健康函数                                 |
| `pnpm --dir apps/cloud-api test`                                                      | JUnit 随机端口下的 HTTP 健康响应         |
| `pnpm test:e2e`                                                                       | 浏览器中的静态页面；不覆盖跨服务诊断     |

运行结果应在任务交付报告中附实际退出状态，区分已通过、失败、工具缺失和未执行。代码未修改，无本次新增行为测试；健康命令的实际执行用于核对本文描述。由于初始化文件尚未跟踪，`git diff --check` 不会覆盖全部未跟踪内容，须结合本文的显式格式检查及文件清单确认写集。

### 本轮交付记录（2026-09-18）

状态：`DONE_WITH_CONCERNS`。唯一新增文件为指定隔离工作区中的 `docs/architecture/001-cloud-edge-diagnostics-skeleton.md`；未修改已有源代码或配置，未提交、推送或创建 PR。

| 实际执行的命令                                                                                  | 结果                                                                                                              |
| ----------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `pnpm validate`                                                                                 | 退出 1：Corepack 尝试创建用户缓存目录时遭遇权限错误，未进入质量门禁                                               |
| `pnpm exec prettier --write docs/architecture/001-cloud-edge-diagnostics-skeleton.md`           | 同上，随后使用工作区已安装的可执行文件完成格式化                                                                  |
| `pnpm exec cspell docs/architecture/001-cloud-edge-diagnostics-skeleton.md`                     | 同上，随后使用工作区已安装的可执行文件检查                                                                        |
| `./node_modules/.bin/prettier --check docs/architecture/001-cloud-edge-diagnostics-skeleton.md` | 退出 0，文档格式通过                                                                                              |
| `./node_modules/.bin/cspell docs/architecture/001-cloud-edge-diagnostics-skeleton.md`           | 退出 1，启动命令中的 Python 路径环境变量（两处）及 Maven 参数前缀（一处）未在词典内；保留正确命令，不修改质量配置 |
| 在 `apps/web` 执行 `../../node_modules/.bin/vitest run`                                         | 退出 0，2 项测试通过                                                                                              |
| `./node_modules/.bin/vitest run packages/contracts/test packages/test-fixtures/test`            | 退出 0，2 项测试通过                                                                                              |
| 在两个 Python 应用分别执行 `python3 -m pytest -p no:cacheprovider`                              | 均退出 1，当前解释器没有 pytest                                                                                   |
| 在两个 Python 应用分别执行 `python3 -m ruff format --check src tests`                           | 均退出 1，当前解释器没有 Ruff                                                                                     |
| 上表两个 Python 模块启动命令，附加禁止写入字节码的环境设置                                      | 均退出 0，输出各自预期健康 JSON                                                                                   |
| `git diff --check`                                                                              | 退出 0；未跟踪文件限制如上                                                                                        |
| `java -version` 及 Maven 命令可用性检查                                                         | Java 退出 1，无可用运行时；Maven 不在当前命令路径中                                                               |

已验证文档与已读代码的入口、职责和健康语义一致，现有 JavaScript 单元测试通过，Python 本地入口可执行。未验证云端 HTTP 健康、JUnit、Python 单元测试、浏览器端到端、完整 lint/typecheck/build 和全量质量门禁；未安装依赖或访问外部网络。后续由工具链维护线补齐环境后重跑门禁，并由文档维护线核对缺失的根说明和架构索引。生产能力及跨服务主链路仍未实现，不在本轮验收范围内。
