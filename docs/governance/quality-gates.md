# 质量门禁规范

## 目的与适用范围

本规范定义仓库在本地和持续集成（CI）中的质量门禁、工具链准备方式及验证报告要求。它适用于管理端、云端 API、边端服务、终端模拟器、跨服务契约及其自动化脚本，不定义或改变业务行为。

本规范与 `AGENTS.md` 一起适用；如有冲突，按 `AGENTS.md` 的规范优先级处理。

## 全量入口与执行原则

`pnpm validate` 是唯一全量质量入口。它必须顺序或并行编排所有适用门禁，并在任一子命令失败时以非零状态退出。只有一次实际成功执行的 `pnpm validate`，才能在验证报告中作为“全量质量门禁已通过”的证据。

以下命令可用于定位或快速反馈，但它们均不能替代全量结论：

| 命令 | 最低覆盖范围 |
| --- | --- |
| `pnpm lint` | ESLint，以及 Python 代码的 ruff lint |
| `pnpm format:check` | Prettier 格式检查，以及适用的 Python 格式检查 |
| `pnpm spellcheck` | cspell |
| `pnpm typecheck` | 前端 TypeScript 检查、Python mypy，以及适用的 Java 编译/类型检查 |
| `pnpm test` | Vitest、Spring Boot JUnit 5、pytest 与契约测试 |
| `pnpm test:e2e` | Playwright 关键用户链路 |
| `pnpm build` | 各可构建组件的生产构建 |

新增应用、语言或测试层时，必须将对应质量命令纳入上述脚本及 `pnpm validate`；不得只在开发者本机手工运行。门禁脚本应输出足以定位失败的日志，并避免输出凭据、令牌或真实生产数据。

## 必需门禁

### 代码质量与一致性

- JavaScript/TypeScript/Vue 使用 ESLint；格式使用 Prettier。
- 文档、配置和用户可见文本使用 cspell；新增专业术语应通过受审查的词典配置处理，不得关闭整文件检查。
- Python 服务和模拟器保留 ruff 与 mypy；规则、目标 Python 版本和忽略项必须可审查。
- Spring Boot 云端 API 使用 JUnit 5；测试失败必须使对应 pnpm 门禁失败。

### 测试层级

- Web 单元与组件测试使用 Vitest（可配合 Vue Testing Library）。
- 浏览器关键链路使用 Playwright，并覆盖必要的加载、错误和主要成功路径。
- Python 服务使用 pytest，覆盖成功、非法输入和异常路径。
- Spring Boot 使用 JUnit 5；跨服务字段和序列化约定使用 schema/契约测试。

### CI 执行

CI 必须同时在 `push` 和 `pull_request`（PR）事件触发。CI 使用锁文件进行确定性依赖安装，例如 `pnpm install --frozen-lockfile`；若某个语言运行时另有锁文件，应采用其等价的锁定安装方式。

CI 必须执行 `pnpm validate`，不得用零散命令替代。失败时保留足以诊断问题的日志、测试报告、覆盖率结果（如已启用）和 Playwright 失败证据（如截图、视频、trace）；产物中不得包含秘密或个人数据。

## 本地工具链准备

开始验证前先检查项目声明的版本与可用命令：

```sh
node --version
corepack --version
pnpm --version
python3 --version
java --version
```

缺少 Node 包管理器时，先安装项目约定的 Node.js 版本并执行 `corepack enable`，再使用 Corepack 提供的 pnpm。依赖清单和锁文件已经存在时，使用 `pnpm install --frozen-lockfile` 安装；不要在验证过程中无故更新锁文件。

缺少 Python 工具时，按各 Python 应用的受版本控制依赖说明创建隔离环境并安装开发依赖，以获得 pytest、ruff 和 mypy。缺少 Java 工具时，安装项目声明的 JDK，并通过云端 API 的受版本控制构建包装器或构建配置运行 JUnit。缺少浏览器依赖时，按 Playwright 的受版本控制配置安装其浏览器二进制。

仓库尚未提供上述版本声明、依赖清单、锁文件或脚本时，禁止猜测命令或伪造通过结果：记录为环境限制，并在相应实现任务中补齐可复现配置。

## 提交与例外

agent 禁止自动执行 `git commit`、`git push`、创建 PR 或改写历史。完成修改后只提供可审查 diff 和验证报告。经人工审阅后，提交者使用 `pnpm commit` 生成提交信息，并由 Commitizen/Commitlint 完成规范校验。

任何暂时无法执行的门禁必须在任务计划、CI 配置或验证报告中明确原因、影响范围、风险接受者和补齐计划。不得以跳过、静默忽略、降低阈值或关闭规则的方式绕过门禁。

## 验证报告模板

每次交付报告至少包含以下分组，并对每条命令给出实际结果（通过、失败、未运行或不适用）及必要的输出摘要：

### 已验证

- 运行的命令及其实际退出状态。
- 已覆盖的文件、组件或质量门禁。
- `git diff --check` 的实际结果。

### 未覆盖

- 未运行的适用测试、构建、端到端链路或健康检查。
- 尚未具备的 CI 产物、阈值或自动化覆盖。

### 环境限制

- 缺失的运行时、包管理器、锁文件、依赖、服务、浏览器或外部凭据。
- 该限制对验证结论的影响，以及可复现的准备或补齐步骤。

报告不得把未运行、被跳过或因环境失败的命令描述为通过；没有新鲜命令证据时，不得声称全量门禁已通过。
