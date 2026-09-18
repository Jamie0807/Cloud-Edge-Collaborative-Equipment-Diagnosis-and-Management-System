# CI 质量门禁

CI 在每次 push 和 Pull Request 上运行根目录唯一全量入口：

```bash
pnpm validate
```

工作流会准备 Node.js/pnpm、Python/pytest/ruff/mypy、Java/Maven 和 Playwright Chromium，然后执行统一门禁。门禁失败时禁止合并；本地开发应先复现失败项并修复后再提交。

Playwright 安装在 `apps/web` workspace 中执行，避免根 workspace 没有直接声明 `@playwright/test` 时出现命令解析错误。

CI 不执行自动提交、自动推送或自动创建 Pull Request。提交仍由开发者显式运行 `pnpm commit` 完成。
