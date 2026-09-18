# 001 云边协同设备诊断管理任务拆分

**状态：** Ready for implementation review — 业务编码尚未开始。
**依赖规格：** [`spec.md`](spec.md)
**依赖计划：** [`plan.md`](plan.md)
**未决来源：** [`../../docs/requirements/001-cloud-edge-diagnostics-analysis.md`](../../docs/requirements/001-cloud-edge-diagnostics-analysis.md) D-001 至 D-014。

## 0. 全局前置条件和完成规则

所有实现任务须在下列前置条件满足后才可开始：

1. D-001 至 D-014 已由用户确认或在用户授权下采用调研推荐值；选择已回写到批准的 spec/plan，并由 ADR 记录长期决定。
2. 已集成治理 bootstrap：`apps/*`、`packages/*`、质量脚本、测试基础设施和 `pnpm validate` 可用。
3. 每个实现任务在隔离 worktree 中执行，只改本任务写集；不得自动 commit、push 或创建 PR。
4. 所有跨服务契约和测试均断言 `assetId`、`terminalId`、`edgeId`、`eventId` 是四个独立字段，且路径遵循终端→边端→云端→Web。
5. 每项行为先写失败测试（RED），再最小实现（GREEN），再重构；命令输出作为验收证据。

路径均为未来实现写集。当前分析任务的实际写集仅为本 feature 的三份 Draft 文档和需求分析文档，未创建任何下列代码/契约目录。

## 1. 任务总览与依赖

| ID    | 任务                             | 依赖              | 对应需求                         |
| ----- | -------------------------------- | ----------------- | -------------------------------- |
| T-001 | 确认接口、ID、存储与认证决策     | 全部 D-001～D-014 | FR-001～FR-012、NFR-001～NFR-005 |
| T-002 | 跨服务契约与共享测试夹具         | T-001、bootstrap  | FR-003、FR-006～FR-010、NFR-002  |
| T-003 | 终端模拟器                       | T-002             | FR-001～FR-003                   |
| T-004 | 边端接入、文件、算法与 outbox    | T-002、T-003      | FR-002、FR-004～FR-007           |
| T-005 | 云端持久化、上报、离线和查询 API | T-002、T-004      | FR-008～FR-012                   |
| T-006 | Vue 管理端                       | T-005             | FR-010～FR-011、NFR-006          |
| T-007 | 分层测试与全链路验证             | T-002～T-006      | 全部                             |
| T-008 | 启动、联调、架构和交付文档       | T-001～T-007      | NFR-001、NFR-003、NFR-005        |

T-003 完成可验证的终端契约后，T-004 才开始真实接入；T-005 必须等待 T-004 的上报载荷和 outbox 状态稳定；T-006 在 T-005 稳定查询 API 后开始。仅允许独立的文档、契约 fixture 和审计任务并行，各实现任务必须有不重叠写集。

## 2. 任务明细

### T-001：确认并冻结实现决策

**依赖：** 已批准的治理设计、分析文档。
**预期写集：**

- 修改：`specs/001-cloud-edge-diagnostics/spec.md`
- 修改：`specs/001-cloud-edge-diagnostics/plan.md`
- 修改：`docs/requirements/001-cloud-edge-diagnostics-analysis.md`
- 可创建（仅有长期架构决定时）：`docs/adr/00x-*.md`

**工作与验收：**

1. 核对 D-001 至 D-014 的确认/授权记录，不得用未记录的默认值实现。
2. 将已确认协议、技术、存储、认证、文件 URI、时间、幂等/重试、分页和资源指标口径写入规格和计划；长期选择记录 ADR。
3. 明确 `eventId` 的生成方、重放语义、唯一性约束和失败重试终态；明确云端以接收时间执行超 60 秒离线规则。
4. 更新状态为可实现前，核对用户故事、接口、数据表、任务和测试均无冲突。

**验证命令：**

```bash
rg -n "D-00[1-9]|D-01[0-4]|assetId|terminalId|edgeId|eventId|60 秒|60 seconds|幂等|认证|文件存储" \
  docs/requirements/001-cloud-edge-diagnostics-analysis.md \
  specs/001-cloud-edge-diagnostics/{spec,plan,tasks}.md
git diff --check
```

**通过标准：** 所有选择有明确确认/授权记录；无隐含技术假设；差异无空白错误。

### T-002：定义跨服务契约与共享夹具

**依赖：** T-001、已集成的 `packages/contracts` 与 `packages/test-fixtures` 骨架。
**预期写集：**

- 创建/修改：`packages/contracts/src/**/*.ts`（或已确认语言的 schema 文件）
- 创建/修改：`packages/contracts/tests/**/*.test.*`
- 创建/修改：`packages/test-fixtures/**/*`
- 修改：`packages/contracts/README.md`

**工作与验收：**

1. 先为 terminal heartbeat、检测上传元数据、edge status、diagnostic event、查询参数/响应写 schema 失败测试。
2. 定义 ID 类型/字段、模态和严重等级枚举、UTC 时间、证据 URI、错误载荷与幂等响应；四个 ID 均必填且不共用含义。
3. 提供红外、声纹、局放的安全文件夹具及有效、缺 ID、错误模态、非法时间、重复 `eventId` fixture；不放真实敏感文件。
4. 发布给四个服务的版本化契约说明，禁止服务私自复制或漂移载荷定义。

**验证命令：**

```bash
pnpm --filter ./packages/contracts test
pnpm --filter ./packages/contracts typecheck
rg -n "assetId|terminalId|edgeId|eventId|eventId.*unique|event_id" packages/contracts packages/test-fixtures
```

**通过标准：** schema 测试覆盖成功/非法/重放载荷；每个跨服务事件保存四 ID；在已集成的 workspace 中命令有真实通过输出。

### T-003：实现终端模拟器

**依赖：** T-002、D-001、D-008、配置格式确认。
**预期写集：**

- 创建/修改：`apps/terminal-simulator/src/**` 或已确认的 Python 包目录
- 创建/修改：`apps/terminal-simulator/tests/**`
- 创建/修改：`apps/terminal-simulator/config/**`
- 修改：`apps/terminal-simulator/README.md`

**工作与验收：**

1. RED：为三终端配置、10 秒心跳、5/20/60 秒采集、四 ID 元数据和仅访问 edge URL 的行为编写 pytest。
2. GREEN：实现可配置调度和夹具文件生成；每个事件生成/保留同一 `eventId` 直到边端接收响应。
3. 将心跳作为 JSON、检测事件作为已确认协议的文件+元数据发送给边端；不得有 cloud URL 客户端。
4. 对连接失败、超时和不被重试的校验错误产生可观察日志，不泄露 API key。

**验证命令：**

```bash
pytest apps/terminal-simulator/tests -q
rg -n "5|20|60|10|assetId|terminalId|edgeId|eventId" apps/terminal-simulator
rg -n "cloud" apps/terminal-simulator --glob '!README.md'
```

**通过标准：** pytest 覆盖三个周期、心跳、失败与 ID 载荷；静态检查未发现终端业务请求云端的实现路径。

### T-004：实现边端接入、文件处理、模拟分析与 outbox

**依赖：** T-002、T-003、D-001～D-003、D-007、D-009～D-012。
**预期写集：**

- 创建/修改：`apps/edge-service/src/**` 或已确认的 Python 包目录
- 创建/修改：`apps/edge-service/tests/**`
- 创建/修改：`apps/edge-service/migrations/**`（仅在 SQLite/本地持久方案确认后）
- 创建/修改：`apps/edge-service/config/**`
- 修改：`apps/edge-service/README.md`

**工作与验收：**

1. RED：为心跳记录、元数据标准化、缺失 ID、模态/时间错误、路径穿越、超限文件、安全保存、算法成功/异常、outbox 状态迁移和云端不可用重试写 pytest。
2. GREEN：实现终端接入端点，使用服务端受控名称保存文件，记录接收时间和终端状态；算法只接收受控保存路径。
3. 组装完整诊断事件，持久化 outbox，并按确认策略发送 edge status 和诊断结果到云端；成功确认后才标记送达。
4. 重放同一 `eventId` 时保持同一业务事件；失败记录关联 ID、错误类型和下次重试时间，不记录凭据/文件正文。

**验证命令：**

```bash
pytest apps/edge-service/tests -q
pytest apps/edge-service/tests -q -k "invalid or path or algorithm or outbox or retry"
rg -n "assetId|terminalId|edgeId|eventId|outbox|retry" apps/edge-service
```

**通过标准：** 边端对成功、非法输入、算法异常、云端不可用都有测试证据；无客户端路径直接拼接到受控文件根目录外；缓存可重放。

### T-005：实现云端持久化、幂等接收、离线判定和查询 API

**依赖：** T-002、T-004、D-002、D-004、D-006、D-008～D-014。
**预期写集：**

- 创建/修改：`apps/cloud-api/src/main/java/**`
- 创建/修改：`apps/cloud-api/src/main/resources/db/migration/**`
- 创建/修改：`apps/cloud-api/src/test/java/**`
- 创建/修改：`apps/cloud-api/src/test/resources/**`
- 修改：`apps/cloud-api/README.md`

**工作与验收：**

1. RED：为 edge status 接收、59/60/61 秒离线边界、重复 `eventId`、关系不存在、组合筛选、空结果和统一错误响应写 JUnit 5 测试。
2. GREEN：迁移创建资产、终端、边端、状态报告、诊断事件关系；诊断表按已确认的 `eventId` 唯一约束去重。
3. 实现边端状态/诊断接收端点和查询/详情端点；云端使用自己的接收时间计算边端状态。
4. 存储证据 URI/hash 而不读取边端路径；实现认证/授权和审计日志时遵循 D-008。

**验证命令：**

```bash
pnpm --filter ./apps/cloud-api test
pnpm --filter ./apps/cloud-api build
rg -n "eventId|assetId|terminalId|edgeId|60|receivedAt|received_at" apps/cloud-api
```

**通过标准：** JUnit 至少有两项有效测试且覆盖离线临界值、幂等和查询；迁移/实体/API 均保留四 ID；在已集成的 workspace 中命令真实通过。

### T-006：实现 Vue 管理端

**依赖：** T-005、D-005、D-007、D-008、D-013。
**预期写集：**

- 创建/修改：`apps/web/src/views/**`
- 创建/修改：`apps/web/src/components/**`
- 创建/修改：`apps/web/src/services/**`
- 创建/修改：`apps/web/src/**/*.test.ts`
- 创建/修改：`apps/web/e2e/**`
- 修改：`apps/web/README.md`

**工作与验收：**

1. RED：为边端列表字段、诊断列表字段/筛选请求、详情证据地址、加载/空/错误状态写 Vitest + Vue Testing Library。
2. GREEN：通过 cloud API client 实现边端列表、诊断列表和详情页面；浏览器中不嵌入 DB 访问或 60 秒判断逻辑。
3. 诊断列表可按 `assetId`、`edgeId`、模态筛选，并显示 `terminalId` 和 `eventId` 关联信息；详情显示完整四 ID 和证据地址。
4. 用 Playwright 覆盖云端有测试数据时的筛选→详情关键链路，以及空/错误状态之一。

**验证命令：**

```bash
pnpm --filter ./apps/web test
pnpm --filter ./apps/web test:e2e
pnpm --filter ./apps/web build
```

**通过标准：** 组件测试和 E2E 证明三页要求、筛选和关键 UI 状态；在已集成的 workspace 中所有已适用命令真实通过。

### T-007：执行契约、故障与全链路验证

**依赖：** T-002～T-006、可启动的本地依赖。
**预期写集：**

- 创建/修改：`tests/integration/001-cloud-edge-diagnostics/**`
- 创建/修改：`docs/verification/001-cloud-edge-diagnostics.md`

**工作与验收：**

1. 运行红外、声纹、局放各一条事件经过终端→边端→云端→Web 的演练，断言四个 ID 值逐段一致。
2. 模拟云端短暂不可用，断言边端文件和 outbox 被保留；恢复后同一 `eventId` 只在云端出现一次。
3. 验证 60 秒离线边界、非法上传、算法异常、查询无结果和 Web API 错误。
4. 运行全量质量入口、差异检查、敏感信息/冲突标记扫描，将实际结果与未运行门禁写入验证报告。

**验证命令：**

```bash
pnpm test
pnpm test:e2e
pnpm validate
git diff --check
rg -n "<{7}|={7}|>{7}|TO[D]O|TB[D]|FIXM[E]|sk-[A-Za-z0-9]" --glob '!pnpm-lock.yaml' .
```

**通过标准：** 报告包含命令、实际结果、通过范围、失败/未运行项和环境限制；不以手工验证替代自动化证据。

### T-008：完成运行、联调与交付文档

**依赖：** T-001～T-007。
**预期写集：**

- 创建/修改：`README.md`
- 创建/修改：`docs/architecture/001-cloud-edge-diagnostics.md`
- 创建/修改：`docs/api/001-cloud-edge-diagnostics.md`
- 创建/修改：`docs/runbooks/001-local-start-and-operations.md`
- 创建/修改：`docs/delivery/001-cloud-edge-diagnostics.md`

**工作与验收：**

1. 记录架构边界、四个 ID 语义、终端→边端→云端→Web 流程、协议、文件路径和不重试/可重试错误。
2. 提供可复制的本地启动、配置、数据库迁移、测试、验收和故障恢复步骤；将所有凭据留在环境变量/示例中，不能填入真实值。
3. 记录 AI 产出、人工确认的 D-001～D-014 决策、未完成内容和下一步，而不夸大自动化结果。
4. 审查交付物与 spec→plan→tasks→files→tests 的可追踪性，并由用户决定后续提交。

**验证命令：**

```bash
rg -n "assetId|terminalId|edgeId|eventId|终端.*边端.*云端.*Web|60 秒|60 seconds" \
  README.md docs/architecture docs/api docs/runbooks docs/verification
git diff --check
pnpm validate
```

**通过标准：** 文档能独立指导启动、验收和故障恢复；追踪关系完整；仅报告实际运行的命令结果。

## 3. 任务边界和当前限制

- 任务 D-001 至 D-014 是决策任务，不能被“先写再改”的代码替代。
- T-002 的 `packages/contracts` 是未来实现写集；本分析 worktree 不创建该目录或任何 schema 文件。
- bootstrap 已集成并由根目录 `pnpm validate` 验证通过；但本 feature 的业务验收命令仍属于未来任务，当前骨架门禁通过不等于业务功能完成。
- 任何任务若发现跨服务 ID 语义、文件归属、认证或重试行为与批准规格冲突，必须停止扩展并请求决策。
