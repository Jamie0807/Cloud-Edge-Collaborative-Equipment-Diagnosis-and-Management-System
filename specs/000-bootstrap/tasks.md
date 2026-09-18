# Bootstrap Tasks：项目研发治理基线

> 本清单执行 [`spec.md`](./spec.md) 和 [`plan.md`](./plan.md)，并受 [`../../.specify/memory/constitution.md`](../../.specify/memory/constitution.md) 约束。

## 依赖

- 已读取并遵守根目录 `AGENTS.md`、批准治理设计和项目 bootstrap plan。
- 原始面试题 `09-ai-fullstack-interview-coding-exercise.md` 仅作为后续业务 spec 输入。
- 本任务不依赖 pnpm 安装，不修改运行时代码。

## 写集

- 允许写入：`.specify/memory/constitution.md`、`.specify/templates/*.md`、`specs/000-bootstrap/*.md`、`docs/architecture/README.md`、`docs/adr/README.md`、`docs/runbooks/README.md`。
- 只读输入：`AGENTS.md`、批准设计、批准计划、原始面试题。
- 禁止写入：业务源码、pnpm 配置、CI workflow、skills 源码、其它 README、原始面试题及其它 worktree；本任务允许清单中的三个文档入口 README 除外。

## 任务清单

- [x] T-001 写入 10 条可验证 Constitution 条款（对应 FR-001/AC-001）。
- [x] T-002 写入 spec、plan、tasks 三个可复用模板（对应 FR-002/AC-002）。
- [x] T-003 编写 bootstrap spec/plan/tasks，覆盖 AGENTS、pnpm workspace、Vitest、Playwright、JUnit、pytest、CI、skills、文档、验收和原始面试题输入（对应 FR-003/FR-004/FR-006/AC-003）。
- [x] T-004 写入 architecture、ADR、runbooks 文档入口（对应 FR-005/AC-004）。
- [x] T-005 运行验证命令并将实际结果补入交付报告（对应 AC-005）。

## 验证命令

```bash
rg -n "AGENTS|constitution|spec|plan|tasks|Vitest|Playwright|JUnit|pytest|pnpm validate|CI|skills" .specify specs/000-bootstrap
git diff --check
```

预期：两条命令均 exit code 0；关键词覆盖需求、计划或任务；无空白错误或冲突标记。

## 验收证据

| AC/任务 | 文件/测试 | 命令与实际结果 | 状态 |
| --- | --- | --- | --- |
| AC-001 | `constitution.md` | `rg ...` exit 0；10 条原则均含强制要求和验证方式 | Passed |
| AC-002 | `.specify/templates/*.md` | `rg ...` exit 0；范围、用户故事、功能/非功能、契约、验收、范围外、未决问题及计划/任务章节存在 | Passed |
| AC-003 | `specs/000-bootstrap/*.md` | `rg ...` exit 0；三文件互链并覆盖指定治理关键词 | Passed |
| AC-004 | `docs/*/README.md` | 文件存在；`git diff --check` exit 0 | Passed |
| AC-005 | 本任务验证命令 | `rg ...` exit 0；`git diff --check` exit 0 | Passed |

## 交付与风险

- 修改文件绝对路径：见 brief 的 10 个目标文件。
- 未覆盖：运行时服务、pnpm workspace、CI、skills 和业务功能；它们属于后续任务。
- 剩余风险：文档完成不等于后续门禁已接入，需由后续任务实现并运行新鲜质量证据。
- 报告路径：`/private/tmp/interview-task-2-report.md`。
