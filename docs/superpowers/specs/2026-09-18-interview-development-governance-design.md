# 云边协同诊断系统研发治理基线设计

**日期：** 2026-09-18
**状态：** 已批准，待实现
**范围：** 项目初始化阶段的研发体系、工程骨架与质量门禁

## 1. 背景与目标

当前目录只有业务需求说明，没有源码、包管理器、CI、测试体系或 AI 协作规范。本阶段的目标不是直接实现完整业务，而是建立可被 AI 和团队重复使用、可自动验证、可持续沉淀的研发基线。

首期交付“治理基线 + 可运行 Monorepo 骨架”，为后续云边协同设备诊断系统的需求分析、实现、测试和验收提供统一入口。

## 2. 已确认的边界

- Git 已在当前目录初始化，默认分支为 `main`；当前没有远程仓库和首个 commit。
- 使用 pnpm Monorepo 作为仓库级工程组织方式。
- 前端使用 Vue 3 + TypeScript + Vite。
- 保留 Spring Boot 云端 API、Python 边端服务、Python 终端模拟器的服务边界。
- 使用轻量本地 Spec Kit 结构，不依赖外部 CLI。
- 建立 GitHub Actions push/PR 质量门禁。
- 前端使用 Vitest 单元/组件测试与 Playwright E2E。
- 后端保留 Spring Boot JUnit 和 Python pytest 门禁。
- 采用 ESLint、Prettier、cspell、Commitlint、Commitizen、Husky。
- `pnpm validate` 是唯一全量质量入口。
- 不自动执行 `git commit`、`git push` 或创建 PR；用户审阅后使用 `pnpm commit` 提交。
- 本阶段不实现完整业务链路，业务功能必须通过后续 feature spec 进入开发。

## 3. 目标目录与职责

```text
apps/
  web/                 # Vue 3 管理端
  cloud-api/            # Spring Boot 云端 API
  edge-service/         # Python 边端服务
  terminal-simulator/   # Python 感知终端模拟器
packages/
  contracts/            # 跨服务接口、事件和数据契约
  test-fixtures/        # 共享测试数据和模拟采集文件
infra/
  mysql/                # 数据库初始化/迁移资源
  docker-compose.yml
.specify/
  memory/constitution.md
  templates/
  scripts/
specs/
  000-bootstrap/        # 本次初始化的 spec/plan/tasks
docs/
  architecture/         # 架构与边界文档
  adr/                   # 架构决策记录
  api/                   # 接口说明
  runbooks/              # 启动、联调和排障手册
skills/                  # 团队可复用 skills 源码
.github/workflows/       # GitHub Actions
AGENTS.md
```

服务边界要求：前端不直接访问数据库；云端负责云端持久化和查询；边端负责终端接入、文件保存、元数据标准化、算法调用和待上报缓存；终端模拟器只能访问边端；所有跨服务契约必须保留 `assetId`、`terminalId`、`edgeId`、`eventId` 的独立语义。

## 4. Spec Kit / SDD 生命周期

项目采用 Constitution → Specify → Clarify → Plan → Tasks → Implement → Verify/Analyze 的生命周期：

1. `constitution.md` 定义项目原则和不可违反的工程约束。
2. `spec.md` 描述用户故事、功能需求、非功能需求、验收标准和范围外内容。
3. `plan.md` 描述架构、接口、数据、测试、风险和迁移策略。
4. `tasks.md` 将计划拆成带文件范围、依赖关系和验证命令的独立任务。
5. 实现阶段使用 TDD、隔离 worktree 和多智能体并行。
6. 验收阶段验证需求追踪、测试、构建、运行、文档和差异质量。

每个 feature 必须保留 `spec.md`、`plan.md`、`tasks.md`；产生长期架构决策时补充 ADR。`specs/000-bootstrap` 只记录本次初始化，不宣称完整业务已实现。

## 5. Constitution 原则

1. 规格先于实现：没有确认的 spec、验收标准和计划，不写生产代码。
2. 测试先于代码：新行为必须先观察失败测试，再写最小实现并重构。
3. 边界清晰：服务通过契约通信，禁止跨服务直接读库或绕过边端链路。
4. 可验证交付：完成声明必须由新鲜命令输出、测试结果或构建证据支持。
5. 自动化门禁：push 和 PR 必须通过格式、拼写、静态检查、测试和构建。
6. 可追溯变更：需求、计划、任务、文件、测试和验收结果可以互相追踪。
7. 安全默认：密钥不入库；输入、文件上传、日志和依赖必须经过安全边界检查。
8. 可运行优先：本地提供统一启动、检查、测试和健康检查入口。
9. AI 受约束协作：AI 先读取规范和 spec，只修改任务写集，不扩大权限或范围。
10. 人工最终决策：架构、范围、破坏性操作、外部发布和合并由用户确认。

## 6. 测试与质量门禁设计

前端质量分层：

- Vitest：纯函数、校验、状态转换和单元测试。
- Vitest + Vue Testing Library：组件交互、加载/错误/空状态和筛选行为。
- Playwright：Web 到 Cloud API 的关键用户链路。
- Schema/契约测试：跨服务请求、响应、事件字段和 ID 语义。

后端质量分层：

- Spring Boot：JUnit 5 + Spring Boot Test，覆盖心跳保存/离线判断和诊断结果保存/查询等有效业务行为。
- Python：pytest，覆盖边端元数据标准化、非法输入、算法异常和待上报缓存。
- 构建与运行：服务构建、健康检查和必要的容器化依赖验证。

根脚本提供：

```text
pnpm lint
pnpm format:check
pnpm spellcheck
pnpm typecheck
pnpm test
pnpm test:e2e
pnpm build
pnpm validate
pnpm commit
```

`pnpm validate` 编排全部质量门禁，任何子命令失败都必须失败退出。Husky 只执行快速本地检查和 commit-msg 校验，完整测试、构建和 E2E 由 CI 执行。CI 使用锁文件安装依赖，在 PR 和 push 上运行，并上传必要的失败诊断产物。

## 7. 多智能体与 Worktree 规则

并行任务使用不重叠写集：治理文件、Spec Kit 文档、质量工具、CI 文档/工作流分别隔离。每个 agent 必须返回变更文件、验证命令、实际结果和剩余风险；禁止自动 commit、push、PR 或破坏性命令。

当前仓库无首个 commit，Git 2.50 的 `git worktree add --orphan` 可用于初始化阶段创建空分支。主 agent 负责审查各 worktree diff、处理冲突并集成；首个正式 commit 由用户审阅后手动执行 `pnpm commit`。

## 8. 可复用 Skills

仓库 `skills/` 是团队 skills 源码，使用 `SKILL.md` 及可选 references/scripts/agents 元数据。首期创建：

- `project-bootstrap`：事实勘察和工程基线识别。
- `spec-driven-development`：SDD 产物和阶段门禁。
- `tdd-quality-gates`：前端、Java、Python 测试与 RED/GREEN/REFACTOR。
- `parallel-worktrees`：任务拆分、写集隔离、agent 调度和集成。
- `review-and-verify`：需求追踪、diff 审查、全量验证和证据化交付。

Skills 只保留需要判断的规则，机械约束优先由脚本和 CI 强制；创建和更新 skills 时使用 skill validator，并用压力场景做独立复验。

## 9. 自主验收标准

每个 feature 与本次 bootstrap 必须检查：

- `spec → plan → tasks → files → tests` 需求追踪完整；
- `git diff --check` 通过，无密钥、临时文件和未解释占位符；
- lint、format、spellcheck、typecheck、Vitest/组件、Playwright、JUnit、pytest 结果可追溯；
- 前端、Spring Boot、Python 构建/运行入口可验证；
- 健康检查和关键主链路可运行；
- 启动、联调、测试、AI 协作说明完整；
- 最终报告区分已验证、未覆盖、环境限制和后续计划。

## 10. 非目标与后续

本阶段不实现设备诊断业务、数据库完整模型、终端定时上报、边端算法和管理页面功能。下一阶段应以现有业务需求为输入，先建立业务总 spec，再拆成终端模拟器、边端接入/分析、云端数据管理、Vue 管理端等可独立验收的 feature。
