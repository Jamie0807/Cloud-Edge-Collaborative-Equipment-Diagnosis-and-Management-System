# Bootstrap Plan：项目研发治理基线

> 本计划实现 [`spec.md`](./spec.md)，受 [`../../.specify/memory/constitution.md`](../../.specify/memory/constitution.md) 约束；执行清单与证据见 [`tasks.md`](./tasks.md)。

## 架构

采用不依赖外部 CLI 的本地 Spec Kit 结构：`.specify/memory` 保存 Constitution，`.specify/templates` 保存复用模板，`specs/000-bootstrap` 保存本次初始化的 SDD 产物；`docs/architecture`、`docs/adr`、`docs/runbooks` 提供长期文档入口。后续 pnpm workspace 和服务边界由其它任务实现，本任务只记录其契约。

## 文件映射

| 需求 | 文件 | 证据 |
| --- | --- | --- |
| FR-001 / AC-001 | `.specify/memory/constitution.md` | 10 条条款及验证方式 |
| FR-002 / AC-002 | `.specify/templates/*.md` | 模板章节检查 |
| FR-003 / AC-003 | `specs/000-bootstrap/{spec,plan,tasks}.md` | 互链与关键词检索 |
| FR-004 / AC-003 | bootstrap 三文件 | AGENTS/pnpm/测试/CI/skills/文档关键词检索 |
| FR-005 / AC-004 | `docs/{architecture,adr,runbooks}/README.md` | 入口职责检查 |
| FR-006 | `specs/000-bootstrap/spec.md` | 原始面试题输入与范围外声明 |

## 实施顺序

1. 建立目录并写入 Constitution。
2. 写入 spec、plan、tasks 模板。
3. 编写 bootstrap spec、plan、tasks 的互链、范围和验收。
4. 写入三个文档入口 README。
5. 执行任务指定的关键词追踪和 diff 卫生检查。

## 测试策略

本任务无运行时代码，采用文档验收：用 `rg` 检查 Constitution、SDD 产物和质量工具关键词，用 `git diff --check` 检查格式。后续业务实现必须遵循 TDD，并按适用性接入 Vitest、Playwright、JUnit、pytest、契约测试和 `pnpm validate`；本任务不伪造这些门禁已运行。

## 风险

- R-001：仅有文档入口而未有运行时脚本；缓解：在 spec/plan/tasks 中明确后续任务边界和依赖。
- R-002：模板与治理约束漂移；缓解：模板显式链接 Constitution，bootstrap 三文件互链并保留验收证据。
- R-003：将原始面试题误当作本次完成范围；缓解：明确其仅为后续业务 spec 输入，并列出范围外。

## 回滚

本任务文件均为新增且无外部状态；如用户确认需回滚，由提交者在审阅后撤销本任务新增文件，并重新运行 brief 验证。agent 不执行删除、重置、commit 或 push。

## 追踪

- Spec：[`spec.md`](./spec.md)
- Tasks：[`tasks.md`](./tasks.md)
- Constitution：[`../../.specify/memory/constitution.md`](../../.specify/memory/constitution.md)
