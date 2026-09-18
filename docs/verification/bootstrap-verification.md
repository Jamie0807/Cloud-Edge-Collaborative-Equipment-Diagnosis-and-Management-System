# Bootstrap 验收记录

**状态：** `PASSED_WITH_LOCAL_TOOLCHAIN`
**范围：** 治理基线、Spec Kit、三条并行线的无业务行为架构骨架
**原则：** 本记录只报告实际运行过的命令，不将未运行门禁标记为通过。

## 本地工具链修复

项目已固定到 `pnpm@10.15.1`，并完成本地依赖安装。为保留 Python 与 Java 门禁，本机已准备项目内工具：

- `.venv`：pytest 8.4.2、ruff 0.16.8、mypy 1.19.1，以及两个 Python workspace 的 editable dev 依赖。
- `.tools/jdk17/Contents/Home`：Temurin JDK 17.0.20.1。
- `.tools/maven`：Apache Maven 3.9.9。
- Playwright Chromium：已安装到用户级 `ms-playwright` 缓存。

这些目录均已加入 `.gitignore`，不会进入提交内容。

## 已验证

| 检查                 | 实际结果                                                                                                                       |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| 全量入口             | 使用本地 JDK/Maven/Python/Chromium 执行 `pnpm validate`，lint、format、spellcheck、typecheck、test、test:e2e、build 全部通过。 |
| Vue/Vite 类型检查    | `apps/web` 的 `vue-tsc --noEmit` 通过。                                                                                        |
| Vitest               | Web、contracts、test-fixtures 共 4 个测试通过。                                                                                |
| Python 质量门禁      | ruff、mypy、pytest 通过；edge-service 6 个测试、terminal-simulator 1 个测试通过。                                              |
| Spring Boot 质量门禁 | Maven compile、Spotless check、JUnit/Spring Boot test、package 通过；JUnit 1 个测试通过。                                      |
| Playwright E2E       | Chromium 已安装，1 个 E2E 测试通过。                                                                                           |
| ESLint / Prettier    | `eslint . --max-warnings=0`、`prettier --check .` 通过。                                                                       |
| cspell               | 61 个文件、0 个拼写问题。                                                                                                      |
| Git 空白检查         | `git diff --check` 无输出。                                                                                                    |
| 需求语义扫描         | 除 AGENTS 中明确的治理约束外，业务分析/spec/plan/tasks 已清除面试/演示范围表述。                                               |

## 环境说明

当前 Codex 沙箱曾禁止 WebServer 监听本机端口；本次通过允许项目验收进程监听本地端口后，Playwright E2E 已真实执行并通过。该限制不再是项目依赖问题。CI 使用 `actions/setup-python`、`actions/setup-java` 和 Playwright 安装步骤复现同一门禁。

## 后续门槛

1. 用户确认 D-001 至 D-014，并把生产级协议、身份、存储、恢复、容量和数据生命周期决策写回批准的 spec/plan/ADR。
2. 在新机器按 `docs/runbooks/local-development.md` 准备工具后，设置 `JAVA_HOME` 与 PATH，再运行根目录 `pnpm validate`。
3. 业务代码继续遵循对应 `tasks.md` 的 TDD 顺序，不把当前健康骨架视为业务功能完成。
