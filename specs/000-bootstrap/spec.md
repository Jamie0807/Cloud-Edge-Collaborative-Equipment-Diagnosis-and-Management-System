# Bootstrap Spec：项目研发治理基线

> 本 spec 只描述治理基线与可运行骨架的初始化，不宣称设备诊断业务已实现。
> 计划见 [`plan.md`](./plan.md)，任务见 [`tasks.md`](./tasks.md)，原则见
> [`../../.specify/memory/constitution.md`](../../.specify/memory/constitution.md)。

## 范围

建立可复用的本地 Spec Kit/SDD 结构，为 pnpm workspace、服务边界、测试质量、CI、skills 和项目文档提供可追踪入口。范围包括 Constitution、spec/plan/tasks 模板、本次 bootstrap 产物及 architecture/ADR/runbook 索引。

## 用户故事

作为后续 feature agent，我希望先读取一致的 Constitution、spec、plan 和 tasks 模板，以便在隔离写集内按批准需求实现并提供可复核证据。

## 功能需求

- FR-001：提供 `.specify/memory/constitution.md`，将 10 条已批准原则转为包含原则、强制要求和验证方式的条款。
- FR-002：提供可复用的 `spec-template.md`、`plan-template.md`、`tasks-template.md`，分别覆盖需求、架构计划和执行/证据。
- FR-003：提供 `specs/000-bootstrap/spec.md`、`plan.md`、`tasks.md`，并互相引用。
- FR-004：bootstrap 产物覆盖 `AGENTS.md`、pnpm workspace、Vitest、Playwright、JUnit、pytest、CI、skills、文档和验收。
- FR-005：提供 architecture、ADR、runbooks 的文档入口，供后续补充具体内容。
- FR-006：明确原始面试题 `09-ai-fullstack-interview-coding-exercise.md` 是后续业务 spec 输入；本 bootstrap 不实现业务链路。

## 非功能需求

- NFR-001：文档可在无外部 Spec Kit CLI 的本地仓库中使用。
- NFR-002：需求、计划、任务、文件、测试和验收证据可相互追踪。
- NFR-003：文档不包含密钥、真实生产数据或未解释占位符；所有验证结果必须有命令证据。
- NFR-004：遵守 `AGENTS.md` 的规范优先级、隔离 worktree、TDD、质量门禁和提交限制。

## 数据/接口契约

- 本任务产出的是文档契约，不改变运行时 API。
- 后续业务 spec 必须独立保留 `assetId`、`terminalId`、`edgeId`、`eventId`，并遵守终端→边端→云端边界。
- 规范入口关系：`constitution.md → spec.md → plan.md → tasks.md → files/tests/evidence`。

## 验收标准

- AC-001：10 条原则各自包含强制要求和验证方式，且不把未来业务写成完成事实。
- AC-002：三个模板包含 brief 要求的全部章节。
- AC-003：bootstrap 的 spec、plan、tasks 互相引用，并覆盖 AGENTS、pnpm workspace、测试质量、CI、skills、文档、验收和原始面试题输入。
- AC-004：architecture、ADR、runbooks 三个 README 明确索引职责和后续写入规则。
- AC-005：brief 指定的 `rg` 和 `git diff --check` 均返回 0。

## 范围外

不实现终端模拟器、边端分析、云端 API、Vue 管理页面、数据库完整模型、CI workflow、团队 skills、业务契约或完整 `pnpm validate`；这些是后续任务的输入或产物。

## 未决问题

- 后续业务总 spec 如何拆分终端、边端、云端和 Web feature，须以原始面试题为输入并经用户确认。
- 具体 API、数据库 schema、部署拓扑和健康检查需在对应 feature spec/plan 中确认。
