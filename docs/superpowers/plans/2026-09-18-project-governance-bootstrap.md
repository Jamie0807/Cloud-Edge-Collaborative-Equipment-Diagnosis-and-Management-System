# 项目研发治理基线初始化 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.本计划覆盖项目治理基线，不实现完整设备诊断业务。

**Goal:** 将当前只有业务需求说明的 Git 项目初始化为可被 AI 和团队复用、可自动验证的 pnpm Monorepo 研发基线，并首先落地根目录 `AGENTS.md`。

**Architecture:** 根仓库使用 pnpm workspace 编排 Vue 3 前端、Spring Boot 云端 API、Python 边端服务和 Python 终端模拟器。Spec Kit 采用 `.specify` 的本地轻量结构，规范和 feature 产物分开存放；Skills、质量脚本和 GitHub Actions 组成自动化约束层。

**Tech Stack:** pnpm、Vue 3、TypeScript、Vite、Vitest、Vue Testing Library、Playwright、Spring Boot、JUnit 5、Python、pytest、ESLint、Prettier、cspell、Commitlint、Commitizen、Husky、GitHub Actions、PostgreSQL、Docker Compose。

## Global Constraints

- 规范先于实现：没有确认的 spec、验收标准和计划，不写生产代码。
- 测试先于代码：新行为必须先观察失败测试，再写最小实现并重构。
- 前端使用 Vue 3 + TypeScript + Vite。
- 后端保留 Spring Boot JUnit 和 Python pytest 门禁。
- `pnpm validate` 是唯一全量质量入口。
- 必须采用 ESLint、Prettier、cspell、Commitlint、Commitizen、Husky。
- GitHub Actions 必须覆盖 pull request 和 push。
- 不自动执行 `git commit`、`git push`、创建 PR 或发布外部资源。
- 用户审阅后使用 `pnpm commit` 完成 Conventional Commit。
- AI 只能修改当前任务声明的文件集合，不得扩大范围。
- 当前阶段只建立治理基线和可运行骨架，不实现完整业务链路。
- 现有业务需求文件 `09-ai-fullstack-interview-coding-exercise.md` 是业务需求输入，不得删除或改写其核心要求。

## 文件结构与责任

| 路径                              | 责任                                      |
| --------------------------------- | ----------------------------------------- |
| `AGENTS.md`                       | 所有 agent 的项目级高优先级约束和执行入口 |
| `.specify/memory/constitution.md` | 项目原则与可追踪治理约束                  |
| `.specify/templates/`             | spec、plan、tasks、验收产物模板           |
| `specs/000-bootstrap/`            | 本次初始化的需求、方案和任务产物          |
| `apps/web/`                       | Vue 3 管理端最小可运行入口                |
| `apps/cloud-api/`                 | Spring Boot 最小健康检查入口              |
| `apps/edge-service/`              | Python 边端最小健康检查入口               |
| `apps/terminal-simulator/`        | Python 模拟器最小可运行入口               |
| `packages/contracts/`             | 跨服务契约和 schema                       |
| `packages/test-fixtures/`         | 共享测试夹具和模拟采集文件                |
| `infra/`                          | PostgreSQL 与 Docker Compose 资源         |
| `skills/`                         | 团队可复用 Skills 源码                    |
| `.github/workflows/ci.yml`        | PR/push 质量门禁                          |
| `docs/`                           | 架构、ADR、API、runbook 和验证报告        |

---

### Task 1: 初始化 AGENTS.md 项目级约束

**Files:**

- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/AGENTS.md`
- Read: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/docs/superpowers/specs/2026-09-18-interview-development-governance-design.md`
- Read: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/09-ai-fullstack-interview-coding-exercise.md`

**Interfaces:**

- Consumes: 已批准的治理设计和根目录面试题。
- Produces: 可被后续 agent 直接读取的项目级工作协议；至少包含规范优先级、skills 检查、Grill Me、worktree/多 agent、TDD、质量门禁、提交限制和自主验收。

- [ ] **Step 1: 写入规则文档**

  `AGENTS.md` 必须按以下章节组织：项目目标、规范优先级、工作前检查、需求澄清、SDD 生命周期、多智能体与 worktree、TDD 测试、代码与目录边界、质量命令、Git/提交策略、安全与敏感信息、自主验收、交付报告格式。明确“不自动 commit”，并要求提交者主动运行 `pnpm commit`。

- [ ] **Step 2: 验证覆盖范围**

  Run:

  ```bash
  rg -n "Grill|worktree|agent|TDD|Vitest|Playwright|JUnit|pytest|cspell|pnpm validate|pnpm commit|禁止.*commit|自主验收" AGENTS.md
  ```

  Expected: 每个关键词至少有一个明确约束，且不出现 TODO、TBD 或模糊的“后续补充”。

- [ ] **Step 3: 做文档卫生检查**

  Run: `git diff --check`

  Expected: exit code 0，无空格错误或冲突标记。

### Task 2: 建立 Spec Kit/SDD 本地骨架

**Files:**

- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/.specify/memory/constitution.md`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/.specify/templates/spec-template.md`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/.specify/templates/plan-template.md`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/.specify/templates/tasks-template.md`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/specs/000-bootstrap/spec.md`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/specs/000-bootstrap/plan.md`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/specs/000-bootstrap/tasks.md`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/docs/architecture/README.md`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/docs/adr/README.md`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/docs/runbooks/README.md`

**Interfaces:**

- Consumes: `AGENTS.md` 和已批准设计。
- Produces: 后续 feature 可复用的 constitution/spec/plan/tasks 模板，以及本次初始化的可追踪需求产物。

- [ ] **Step 1: 写入 constitution**

  将 10 条已批准的项目原则原样转化为可验证条款，每条包含原则、强制要求和验证方式；不得把未来业务功能写成已完成事实。

- [ ] **Step 2: 写入模板**

  `spec-template.md` 必须包含范围、用户故事、功能需求、非功能需求、数据/接口契约、验收标准、范围外和未决问题；`plan-template.md` 必须包含架构、文件映射、测试策略、风险和回滚；`tasks-template.md` 必须包含依赖、写集、测试先行步骤、验证命令和验收证据。

- [ ] **Step 3: 编写 bootstrap spec/plan/tasks**

  三个文件必须互相引用，并覆盖 AGENTS、pnpm workspace、测试质量、CI、skills、文档和验收；明确原始业务需求作为后续业务 spec 输入。

- [ ] **Step 4: 验证追踪关系**

  Run:

  ```bash
  rg -n "AGENTS|constitution|spec|plan|tasks|Vitest|Playwright|JUnit|pytest|pnpm validate|CI|skills" .specify specs/000-bootstrap
  git diff --check
  ```

  Expected: 初始化目标全部出现在需求、计划或任务中，命令 exit code 0。

### Task 3: 初始化 pnpm Monorepo 和最小服务骨架

**Files:**

- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/package.json`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/pnpm-workspace.yaml`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/.npmrc`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/apps/web/`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/apps/cloud-api/`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/apps/edge-service/`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/apps/terminal-simulator/`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/packages/contracts/`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/packages/test-fixtures/`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/infra/`

**Interfaces:**

- Consumes: `pnpm` workspace conventions from bootstrap plan。
- Produces: 根目录统一脚本和各服务可独立识别的健康检查/测试入口；不实现业务链路。

- [ ] **Step 1: 写根 package manifest**

  根 `package.json` 使用 `packageManager: "pnpm@10"`，提供 `lint`、`format:check`、`spellcheck`、`typecheck`、`test`、`test:e2e`、`build`、`validate`、`commit` 脚本；`validate` 按顺序调用所有质量脚本并保留失败退出码。

- [ ] **Step 2: 写 workspace 配置**

  `pnpm-workspace.yaml` 只包含 `apps/*` 和 `packages/*`；各 workspace 有自己的 manifest、README 和最小可运行入口。

- [ ] **Step 3: 写最小服务入口**

  Vue 提供可加载的根组件；Spring Boot 提供 `/actuator/health` 或等价健康接口；Python 两个服务提供可执行入口和 pytest 发现路径；契约包提供 ID 字段 schema 示例。

- [ ] **Step 4: 验证 workspace**

  Run: `corepack pnpm install --lockfile-only`

  Expected: 生成 `pnpm-lock.yaml`，workspace 可解析；不执行完整业务构建。

### Task 4: 接入前端/后端测试与代码质量工具

**Files:**

- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/vitest.config.ts`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/playwright.config.ts`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/eslint.config.js`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/prettier.config.mjs`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/cspell.json`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/commitlint.config.cjs`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/.czrc`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/.husky/pre-commit`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/.husky/commit-msg`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/apps/web/src/**/*.test.ts`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/apps/edge-service/tests/`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/apps/cloud-api/src/test/`

**Interfaces:**

- Consumes: Task 3 workspace 入口。
- Produces: 真实可执行的 unit/component/E2E、pytest、JUnit 和静态质量门禁；不是空脚本或永远通过的占位测试。

- [ ] **Step 1: 为 Vue 最小行为写失败测试**

  测试组件渲染项目标题和健康状态；先运行 `corepack pnpm exec vitest run`，确认缺少实现时失败。

- [ ] **Step 2: 写最小 Vue 实现并验证绿色**

  只实现测试所需的根组件和健康状态展示；运行 Vitest，确认测试通过，再进行格式化。

- [ ] **Step 3: 为 Python 标准化入口写 pytest**

  覆盖合法 `assetId`/`terminalId`/`edgeId`/`eventId` 保留，以及缺失字段拒绝；先观察失败，再实现最小校验。

- [ ] **Step 4: 为 Spring Boot 健康/心跳最小行为写 JUnit**

  至少覆盖成功健康响应和一个状态判断；先验证测试失败，再写最小实现。

- [ ] **Step 5: 接入格式、拼写、提交校验**

  使用 ESLint、Prettier、cspell、Commitlint、Commitizen、Husky；`pre-commit` 只运行快速门禁，完整测试留给 CI。

- [ ] **Step 6: 验证质量工具**

  Run: `corepack pnpm lint && corepack pnpm format:check && corepack pnpm spellcheck && corepack pnpm test`

  Expected: 所有命令真实执行并返回 0，测试输出包含前端、Java、Python 的结果；不以 `echo` 或空命令伪造通过。

### Task 5: 建立 GitHub Actions CI 质量门禁

**Files:**

- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/.github/workflows/ci.yml`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/docs/runbooks/ci.md`

**Interfaces:**

- Consumes: 根 `pnpm validate` 和各服务测试/构建入口。
- Produces: PR 和 push 可执行的 CI 门禁、缓存策略、失败诊断和检查项说明。

- [ ] **Step 1: 定义触发器和最小权限**

  监听 `pull_request` 与 `push` 到 `main`；设置最小 `permissions`，使用锁文件安装依赖。

- [ ] **Step 2: 编排质量 job**

  CI 先安装依赖，再运行 `pnpm validate`；需要时启动服务和健康检查后执行 Playwright；Java/Python job 输出各自测试结果。

- [ ] **Step 3: 保存诊断产物**

  失败时上传 Playwright trace、截图、JUnit/pytest 报告和构建日志；不得上传密钥或本地环境文件。

- [ ] **Step 4: 校验 workflow 静态结构**

  Run: `git diff --check && rg -n "pull_request|push|pnpm validate|permissions|playwright|junit|pytest" .github/workflows/ci.yml`

  Expected: 触发器、门禁、权限和测试类型全部存在。

### Task 6: 创建并校验团队 Skills

**Files:**

- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/skills/project-bootstrap/SKILL.md`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/skills/spec-driven-development/SKILL.md`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/skills/tdd-quality-gates/SKILL.md`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/skills/parallel-worktrees/SKILL.md`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/skills/review-and-verify/SKILL.md`
- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/skills/README.md`

**Interfaces:**

- Consumes: `AGENTS.md` 中的流程约束。
- Produces: 带 YAML frontmatter、明确触发条件、任务边界、输入输出和验证方式的仓库内 skills；不得复制通用政策或留下脚手架占位符。

- [ ] **Step 1: 为每个 skill 定义触发条件和边界**

  description 使用 “Use when ...” 形式，正文只保留项目特有判断规则；机械检查引用 `pnpm validate` 或 validator。

- [ ] **Step 2: 写 skills**

  每个 skill 至少给出输入、输出、禁止事项、成功证据和失败处理；`parallel-worktrees` 必须明确不重叠写集，`review-and-verify` 必须明确不得无证据宣称完成。

- [ ] **Step 3: 独立压力复验**

  使用只读或临时 worktree 运行至少一个需求澄清、一个 TDD、一个并行写集和一个验收场景，记录 agent 是否遵守技能边界。

- [ ] **Step 4: 运行 skill validator**

  Run: `python3 /Users/jamie/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/*`

  Expected: 每个 skill 的 frontmatter、命名和内容均通过；失败项修复后重新执行。

### Task 7: 整体自主验收和交付报告

**Files:**

- Create: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/docs/verification/bootstrap-verification.md`
- Modify: `/Users/jamie/Documents/文稿 - Jamie的MacBook Pro/code/interview/README.md`
- Read: all files created by Tasks 1–6

**Interfaces:**

- Consumes: 所有初始化产物和命令输出。
- Produces: 需求追踪、验证证据、限制说明和后续业务拆解入口。

- [ ] **Step 1: 执行完整门禁**

  Run: `corepack pnpm validate`

  Expected: lint、format、spellcheck、typecheck、unit/component、Java、Python、E2E（若环境具备）、build 全部有真实结果；缺失环境必须明确记录而非伪造通过。

- [ ] **Step 2: 检查仓库卫生**

  Run: `git diff --check && git status --short && rg -n "TODO|TBD|FIXME|PLACEHOLDER|sk-[A-Za-z0-9]" --glob '!pnpm-lock.yaml' .`

  Expected: 无格式错误、无未解释占位符、无疑似密钥；`.DS_Store` 由 `.gitignore` 忽略。

- [ ] **Step 3: 编写验证报告**

  报告必须列出已验证通过、未覆盖、环境限制、任务映射、命令和实际输出摘要；明确当前仍未实现业务功能。

- [ ] **Step 4: 更新 README**

  README 说明项目定位、目录结构、前置依赖、`pnpm install`、`pnpm validate`、如何创建 feature spec、如何手动使用 `pnpm commit`，并链接原始业务需求和治理文档。

## 执行顺序与并行策略

1. Task 1 先行，建立所有 agent 必须遵守的 `AGENTS.md`。
2. Task 2 依赖 Task 1，可与 Task 3 的目录骨架准备并行，但不共享写集。
3. Task 3 完成根脚本后，Task 4 和 Task 5 可分别并行；Task 5 依赖 Task 3 的脚本契约。
4. Task 6 可在 Task 1 完成后并行编写，但必须在 Task 7 前通过 validator。
5. Task 7 只在前置任务集成后执行。

所有 agent 都必须在隔离 worktree 中工作，返回实际变更和验证证据；主 agent 不接受“应该通过”或未执行命令的完成声明。除非用户明确要求，计划执行不创建 git commit。
