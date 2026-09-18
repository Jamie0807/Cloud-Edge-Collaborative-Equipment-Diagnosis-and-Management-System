# 云边协同设备诊断系统

这是一个基于 pnpm Monorepo 的云边协同设备诊断系统，包含终端模拟器、边端服务、Spring Boot 云端 API、Vue 3 管理端，以及共享契约和测试夹具。

## 研发入口

所有全量质量检查统一从根目录执行：

```bash
pnpm install
pnpm validate
```

`pnpm validate` 覆盖 ESLint、Prettier、cspell、TypeScript/Python/Java 检查、Vitest、pytest、JUnit、Playwright 和构建。CI 在 push 与 Pull Request 上执行同一入口。

业务开发遵循：

1. 阅读 `AGENTS.md`、`.specify/memory/constitution.md` 和对应 feature 的 `spec.md`、`plan.md`、`tasks.md`。
2. 在隔离 Git worktree 中按 TDD 实现，先 RED、再 GREEN、再 REFACTOR。
3. 通过本地 `pnpm validate` 后，由开发者显式运行 `pnpm commit`；AI 不自动提交、推送或创建 PR。

业务需求基线见 [`09-ai-fullstack-interview-coding-exercise.md`](09-ai-fullstack-interview-coding-exercise.md)，其文件名保留历史路径，但内容按正式产品需求维护。
