# 质量门禁规范

## 目的与适用范围

本规范定义本地和 CI 的质量门禁、工具链准备方式及验证报告要求，适用于 Web、云端 API、边端、终端模拟器、跨服务契约和自动化脚本；不定义业务行为。

本规范与 `AGENTS.md` 一起适用；发生冲突时遵循 `AGENTS.md` 的规范优先级。

## 全量入口

`pnpm validate` 是唯一全量质量入口。它必须在任一子命令失败时以非零状态退出，且只有实际成功执行过的 `pnpm validate` 才能作为全量通过证据。

| 命令                | 覆盖范围                                      |
| ------------------- | --------------------------------------------- |
| `pnpm lint`         | ESLint、Python ruff、Java 编译检查            |
| `pnpm format:check` | Prettier、Python ruff format、Java Spotless   |
| `pnpm spellcheck`   | cspell                                        |
| `pnpm typecheck`    | Vue TypeScript、Python mypy、Java 编译检查    |
| `pnpm test`         | Vitest、契约测试、pytest、Spring Boot JUnit 5 |
| `pnpm test:e2e`     | Playwright 关键用户链路                       |
| `pnpm build`        | Web、Python、Spring Boot 构建                 |

新增语言、应用或测试层时，必须把对应命令纳入上述脚本和 `pnpm validate`；局部命令只能用于定位问题，不能替代全量结论。

## 必需质量层

- JavaScript/TypeScript/Vue 使用 ESLint 和 Prettier，文档与配置使用 cspell。
- Python 保留 pytest、ruff、mypy；Spring Boot 保留 JUnit 5。
- Web 组件测试使用 Vitest/Vue Testing Library，关键用户链路使用 Playwright。
- 跨服务消息使用 schema/契约测试，独立保留 `assetId`、`terminalId`、`edgeId`、`eventId`。

## CI 门禁

CI 必须在 `push` 和 `pull_request` 上触发，使用锁文件进行确定性安装（例如 `pnpm install --frozen-lockfile`），并执行根目录 `pnpm validate`。失败时保留足以诊断问题的测试日志和 Playwright 失败证据；不得包含密钥、令牌或真实生产数据。

## 本地工具链

开始验证前检查 Node/pnpm、Python、Java/Maven 和 Playwright 浏览器。Python 使用各应用 `pyproject.toml` 中的 dev extra；本项目本地可使用 `.venv` 安装 pytest、ruff、mypy。Java 使用 JDK 17 和 Maven；本项目本地工具位于 `.tools` 时，设置：

```bash
export JAVA_HOME="$PWD/.tools/jdk17/Contents/Home"
export PATH="$PWD/.tools/maven/bin:$PWD/.venv/bin:$PATH"
```

Playwright 浏览器按 `apps/web` workspace 的配置安装。依赖或运行时缺失时必须记录为环境限制，不得静默跳过或伪造通过。

## 提交与例外

agent 不得自动执行 `git commit`、`git push`、创建 PR 或改写历史。人工审阅后使用 `pnpm commit`，由 Commitizen/Commitlint 校验 Conventional Commits。暂时无法执行的门禁必须记录原因、影响、风险接受者和补齐计划，不得通过降低阈值或关闭规则绕过。

## 验证报告

每次交付报告至少分为：

- **已验证**：命令、退出状态、覆盖范围和 `git diff --check` 结果。
- **未覆盖**：未运行或不适用的测试、构建、E2E 和健康检查。
- **环境限制**：缺失工具、依赖、服务、浏览器或外部凭据，以及对结论的影响和补齐步骤。
- **剩余风险**：未批准的需求、未实现的行为和后续计划。

没有新鲜命令证据时，不得声称全量门禁通过。
