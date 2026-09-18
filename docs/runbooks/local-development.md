# 本地质量环境

## Python 门禁

项目保留 Python 的 pytest、ruff 和 mypy 门禁。建议使用项目虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e 'apps/edge-service[dev]' -e 'apps/terminal-simulator[dev]'
```

验证：

```bash
python -m pytest apps/edge-service/tests apps/terminal-simulator/tests -q
python -m ruff check apps/edge-service/src apps/edge-service/tests apps/terminal-simulator/src apps/terminal-simulator/tests
python -m mypy apps/edge-service/src apps/terminal-simulator/src
```

## Java 与 Maven

需要 Java 17 和 Maven。项目验收环境可使用 `./.tools` 下的本地工具；如果工具尚未准备，也可以使用系统安装的 Temurin/OpenJDK 17 与 Maven。使用项目本地工具时：

```bash
export JAVA_HOME="$PWD/.tools/jdk17/Contents/Home"
export PATH="$JAVA_HOME/bin:$PWD/.tools/maven/bin:$PWD/.venv/bin:$PATH"
java -version
mvn -version
```

然后执行云端测试：

```bash
mvn -f apps/cloud-api/pom.xml test
```

## Playwright 浏览器

安装 Node 依赖后，在声明 `@playwright/test` 的 Web workspace 中安装 Chromium：

```bash
pnpm --dir apps/web exec playwright install chromium
```

## 全量验收

上述环境就绪后，从仓库根目录执行唯一全量入口：

```bash
pnpm validate
```
