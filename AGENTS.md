# 项目级 AI 开发工作协议

## 项目目标

本项目建设可运行的云边协同设备诊断管理系统：感知终端模拟器只访问边端，边端负责接入、文件保存、元数据标准化、模拟分析和待上报缓存，云端负责持久化、查询和管理端展示。所有跨服务契约必须独立保留 `assetId`、`terminalId`、`edgeId`、`eventId` 的语义。业务实现必须由已批准的 feature spec 进入开发；初始化阶段不以治理文档代替业务功能。

该需求按正式产品系统治理，不以面试、演示时长或一次性样例为范围上限。生产相关的可用性、容量、性能、恢复、认证授权、证据安全、审计、可观测性、迁移回滚和数据生命周期要求必须在需求与 ADR 中明确；暂不纳入的能力必须有版本边界、风险接受和后续计划。

## 规范优先级

规范冲突时按以下顺序处理：用户当前明确指令；已批准的 `constitution.md`、`spec.md`、`plan.md`、`tasks.md`；本文件；架构、API、ADR 和 runbook 文档；代码注释与默认工具行为。发现冲突必须停止扩大范围并报告，不得擅自弱化高优先级约束。未确认的需求不得直接转化为生产代码。

## 工作前检查

开始工作前必须读取本文件、任务 brief 及任务引用的 spec/plan/tasks，并检查仓库状态、当前 worktree、写集和可用命令。若任务匹配某个 skill，必须先读取并遵循其 `SKILL.md`；至少检查项目适用的 Skills、测试要求和验证要求。先确认是否存在敏感信息、未解释占位符或与当前任务重叠的未提交修改。任何 agent 只能修改任务明确授权的文件。

## 需求澄清

使用 Spec-Driven Development（SDD）生命周期处理需求：先确认用户故事、功能和非功能需求、验收标准、范围外内容及风险。需求不完整、验收标准冲突或涉及破坏性操作、架构变更、外部发布时，先向用户澄清；不得用猜测替代确认。需求稳定后才开始实现或文档修改。

## SDD 生命周期

每个 feature 按 `Constitution → Specify → Clarify → Plan → Tasks → Implement → Verify/Analyze` 推进。必须保留 `spec.md`、`plan.md`、`tasks.md`，并在长期架构决策产生时补充 ADR。tasks 必须列出文件范围、依赖、验证命令和验收标准；实现后维护 `spec → plan → tasks → files → tests` 的追踪关系。

## 多智能体与 worktree

两个或更多独立任务才使用多 agent，并按不重叠写集拆分。每个 agent 必须在隔离 worktree 中工作，先确认 worktree 已隔离且目录状态可解释；禁止跨 agent 共享未审查写集。治理文件、Spec Kit 文档、质量工具、CI 文档/工作流应分别隔离。agent 返回时必须报告修改文件、验证命令、实际结果和剩余风险。主 agent 负责审查 diff、处理冲突和集成。

## TDD 测试

新行为遵循 TDD：先写能表达验收标准的失败测试（RED），再写最小实现（GREEN），最后重构并保持测试通过。前端使用 Vitest/Vue Testing Library，关键用户链路使用 Playwright；Spring Boot 使用 JUnit 5，Python 使用 pytest；跨服务字段使用 schema/契约测试。测试必须覆盖成功、非法输入、异常和关键空/加载/错误状态，不能只依赖手工演示。

## 代码与目录边界

目标目录职责固定：`apps/web` 为 Vue 3 管理端，`apps/cloud-api` 为 Spring Boot 云端 API，`apps/edge-service` 为 Python 边端，`apps/terminal-simulator` 为 Python 终端模拟器，`packages/contracts` 为跨服务契约，`packages/test-fixtures` 为共享测试数据。前端不得直连数据库；终端不得直连云端；服务不得绕过边端链路或跨服务直接读库。只修改任务写集，不顺手重排无关文件、升级依赖或扩大业务范围。

## 质量命令

`pnpm validate` 是唯一全量质量入口，必须编排并在任一子命令失败时失败退出。可单独运行的门禁包括：`pnpm lint`、`pnpm format:check`、`pnpm spellcheck`、`pnpm typecheck`、`pnpm test`、`pnpm test:e2e`、`pnpm build`。质量检查还必须覆盖 Vitest、Playwright、JUnit、pytest、cspell 及必要的健康检查；CI 在 push 和 PR 上使用锁文件安装依赖并保留必要诊断产物。提交前不得声称通过未实际运行的命令。

质量门禁的命令映射、工具链准备、CI 触发与验证报告模板以 `docs/governance/quality-gates.md` 为准。任何新增或调整质量脚本、CI 门禁或例外，必须同步更新该文档；不得以局部命令成功替代 `pnpm validate` 的全量结论。

## Git/提交策略

禁止 agent 自动 `git commit`、`git push`、创建 PR、改写历史或执行破坏性命令。完成后仅提供可审查的 diff 和报告；用户审阅后由提交者主动运行 `pnpm commit`，并通过 Commitizen/Commitlint 生成和校验提交信息。除非用户明确授权，不得删除、重置、强制覆盖或清理他人改动。

## 安全与敏感信息

密钥、令牌、个人数据和真实生产文件不得入库或写入日志。所有输入、文件上传、路径、元数据和依赖必须经过安全边界检查；日志不得泄露凭据。发现疑似秘密、越权访问、路径穿越、未验证文件或不安全依赖时立即报告并停止相关扩展。外部网络、发布和权限提升必须得到用户授权。

## 自主验收

完成前必须自主检查：需求追踪完整；`git diff --check` 通过；无未解释占位符、冲突标记、密钥和临时文件；相关 lint、format、spellcheck、typecheck、测试、构建和运行入口有新鲜证据；健康检查和关键主链路在适用时可运行；启动、联调、测试和 AI 协作说明完整。验收报告区分已验证、未覆盖、环境限制和后续计划；没有命令证据不得宣称完成。

## 交付报告格式

每个 agent 最终报告必须包含：状态（`DONE`、`DONE_WITH_CONCERNS` 或 `BLOCKED`）；修改文件的绝对路径；运行的验证命令及每条命令的实际结果；已验证内容；未覆盖内容和环境限制；剩余风险与后续计划。报告应写入任务指定位置，并保持与 worktree diff 一致。不得隐瞒失败、跳过的门禁或未经用户确认的范围变化。
