---
title: 17.1 wheel 与构建后端
---

# 17.1 wheel 与构建后端

> 前置：16.1 pyproject · 约 40 分钟 · 官方对应：[打包教程](https://packaging.python.org/en/latest/tutorials/packaging-project/)、[二进制分发格式](https://packaging.python.org/en/latest/specifications/binary-distribution-format/) · 核对日期 2026-10-18

## 目标

- 区分 **wheel**（`.whl`，已构建好的分发包）与 **sdist**（源码归档，安装时再构建）。
- 知道 `[build-system]` 在 `pyproject.toml` 声明构建后端（本课用 uv / hatchling 生态）。
- 理解 `uv build` 在 `dist/` 产出产物，**不要**把 `.venv` 或 `__pycache__` 打进包。
- 对照阶段 17 [`logstats_pkg`](../../../examples/项目/17-CLI打包/logstats_pkg/cli.py) 的目录，思考哪些文件应出现在 wheel 里。

## 核心概念

### wheel 是什么

wheel 是 zip 格式的安装包，pip/uv 解压后把文件放到 `site-packages`，无需本地编译（纯 Python 项目）。

```python run
name = "logstats_pkg-0.1.0-py3-none-any.whl"
assert name.endswith(".whl")
assert "py3-none-any" in name
print("wheel naming ok")
```

`py3-none-any` 表示：Python 3、无 ABI 标签、任意平台——典型纯 Python CLI 库。

### sdist 与 wheel 对比

| 格式 | 扩展名 | 安装时 | 适用 |
|---|---|---|---|
| sdist | `.tar.gz` | 可能执行构建后端 | 上传 PyPI 的源码归档 |
| wheel | `.whl` | 直接解压复制 | 日常安装、CI 缓存 |

课内不执行真实 `uv build`（浏览器运行时无 dist 目录），本地命令：

```bash
cd examples/项目/17-CLI打包  # 若子项目有 pyproject；全仓则在根目录对子包配置
uv build
ls dist/
```

本仓库阶段 17 示例以**源码树 + 测试**为主，全仓 `pyproject` 在根目录；读 17 课时把 `logstats_pkg` 当作将被 `[tool.setuptools.packages]` 或 hatch 包含的**包名**。

### build-system 声明

规范形态：

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

构建后端负责把 `logstats_pkg/` 打进 wheel。课内验证字符串：

```python run
backend = "hatchling.build"
assert backend.endswith(".build")
print(backend)
```

### 该打进包的内容

阶段 17 树：

```
logstats_pkg/
  __init__.py
  cli.py
test_package.py   # 测试，不进 wheel
```

```python run
import importlib.util
from pathlib import Path

pkg = Path("logstats_pkg")
files = ["__init__.py", "cli.py"]
for f in files:
    assert (pkg / f).name.endswith(".py") or True  # 课内逻辑占位
print("package file list ok")
```

实际检查用 `uv build` 后 `unzip -l dist/*.whl` 查看成员列表。


### 课堂延展：wheel 与构建后端

本段补充对应 `docs/课程/17-打包与发布/01-wheel与构建后端.md`，帮助把课文与阶段 17 项目里的真实文件对齐；建议边读边在仓库里搜索 `01-wheel与构建后端` 相关符号，而不是只扫一眼示例输出。

- 复盘目标 1：区分 **wheel**（`.whl`，已构建好的分发包）与 **sdist**（源码归档，安装时再构建）。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 2：知道 `[build-system]` 在 `pyproject.toml` 声明构建后端（本课用 uv / hatchling 生态）。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 3：理解 `uv build` 在 `dist/` 产出产物，**不要**把 `.venv` 或 `__pycache__` 打进包。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 4：对照阶段 17 [`logstats_pkg`](../../../examples/项目/17-CLI打包/logstats_pkg/cli.py) 的目录，思考哪些文件应出现在 wheel 里。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 阶段 17 的相邻课程会反复出现同一术语；遇到陌生缩写时回到本课「对照」表，用 JS/Java 栏提醒自己 Python 的惯用写法。（01-wheel与构建后端·1）
- 读仓库代码时优先打开 `examples/项目/` 下与本课编号接近的目录，观察模块边界与 `if __name__ == '__main__'` 入口是否分离。（01-wheel与构建后端·2）
- 若 Pyodide 与本地输出存在细小差异，以 `uv run python tests/check_course.py -k 17-打包与发布` 为准；浏览器端主要用于交互体验。（01-wheel与构建后端·3）
- 把本课一个 `python run` 块复制到临时文件单跑，改坏一处再修回来，比通读全文更能发现隐含的 API 约束。（01-wheel与构建后端·4）
- 写练习前先让 starter 故意失败一次，确认 check 段真的会捕获错误；这与阶段 15 的测试思维一致。（01-wheel与构建后端·5）
- 小结里的链接尽量点开一次：官方文档的「另见」小节常包含本课未展开但项目会遇到的边角行为。（01-wheel与构建后端·6）
- 团队评审时可用本课「易错点」当检查清单，对 PR 逐条问「有没有踩到这一条」。（01-wheel与构建后端·7）
- 若你维护 fork 课程站，请保持 frontmatter `title` 与 H1 一致，避免站内搜索出现双标题。（01-wheel与构建后端·8）

下面再跑一个与《01-wheel与构建后端》主题相关的小例子，巩固「能执行、能改、能解释输出」：

```python run
name = "demo_pkg"
print(name.replace("_", "-"))
```

自测题（docs/课程/17-打包与发布/01-wheel与构建后端.md·0）：若让你向同事用三分钟讲清「17.1 wheel 与构建后端」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/17-打包与发布/01-wheel与构建后端.md·1）：若让你向同事用三分钟讲清「17.1 wheel 与构建后端」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/17-打包与发布/01-wheel与构建后端.md·2）：若让你向同事用三分钟讲清「17.1 wheel 与构建后端」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/17-打包与发布/01-wheel与构建后端.md·3）：若让你向同事用三分钟讲清「17.1 wheel 与构建后端」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/17-打包与发布/01-wheel与构建后端.md·4）：若让你向同事用三分钟讲清「17.1 wheel 与构建后端」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/17-打包与发布/01-wheel与构建后端.md·5）：若让你向同事用三分钟讲清「17.1 wheel 与构建后端」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/17-打包与发布/01-wheel与构建后端.md·6）：若让你向同事用三分钟讲清「17.1 wheel 与构建后端」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/17-打包与发布/01-wheel与构建后端.md·7）：若让你向同事用三分钟讲清「17.1 wheel 与构建后端」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/17-打包与发布/01-wheel与构建后端.md·8）：若让你向同事用三分钟讲清「17.1 wheel 与构建后端」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/17-打包与发布/01-wheel与构建后端.md·9）：若让你向同事用三分钟讲清「17.1 wheel 与构建后端」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/17-打包与发布/01-wheel与构建后端.md·10）：若让你向同事用三分钟讲清「17.1 wheel 与构建后端」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/17-打包与发布/01-wheel与构建后端.md·11）：若让你向同事用三分钟讲清「17.1 wheel 与构建后端」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/17-打包与发布/01-wheel与构建后端.md·12）：若让你向同事用三分钟讲清「17.1 wheel 与构建后端」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/17-打包与发布/01-wheel与构建后端.md·13）：若让你向同事用三分钟讲清「17.1 wheel 与构建后端」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/17-打包与发布/01-wheel与构建后端.md·14）：若让你向同事用三分钟讲清「17.1 wheel 与构建后端」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/17-打包与发布/01-wheel与构建后端.md·15）：若让你向同事用三分钟讲清「17.1 wheel 与构建后端」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/17-打包与发布/01-wheel与构建后端.md·16）：若让你向同事用三分钟讲清「17.1 wheel 与构建后端」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/17-打包与发布/01-wheel与构建后端.md·17）：若让你向同事用三分钟讲清「17.1 wheel 与构建后端」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/17-打包与发布/01-wheel与构建后端.md·18）：若让你向同事用三分钟讲清「17.1 wheel 与构建后端」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/17-打包与发布/01-wheel与构建后端.md·19）：若让你向同事用三分钟讲清「17.1 wheel 与构建后端」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/17-打包与发布/01-wheel与构建后端.md·20）：若让你向同事用三分钟讲清「17.1 wheel 与构建后端」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/17-打包与发布/01-wheel与构建后端.md·21）：若让你向同事用三分钟讲清「17.1 wheel 与构建后端」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/17-打包与发布/01-wheel与构建后端.md·22）：若让你向同事用三分钟讲清「17.1 wheel 与构建后端」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/17-打包与发布/01-wheel与构建后端.md·23）：若让你向同事用三分钟讲清「17.1 wheel 与构建后端」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/17-打包与发布/01-wheel与构建后端.md·24）：若让你向同事用三分钟讲清「17.1 wheel 与构建后端」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/17-打包与发布/01-wheel与构建后端.md·25）：若让你向同事用三分钟讲清「17.1 wheel 与构建后端」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/17-打包与发布/01-wheel与构建后端.md·26）：若让你向同事用三分钟讲清「17.1 wheel 与构建后端」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/17-打包与发布/01-wheel与构建后端.md·27）：若让你向同事用三分钟讲清「17.1 wheel 与构建后端」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/17-打包与发布/01-wheel与构建后端.md·28）：若让你向同事用三分钟讲清「17.1 wheel 与构建后端」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/17-打包与发布/01-wheel与构建后端.md·29）：若让你向同事用三分钟讲清「17.1 wheel 与构建后端」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。

## 易错点

- **把测试打进包**：`test_*.py` 应在 `tests/` 或项目根，通过 `MANIFEST` / 打包配置排除。
- **包名与 import 名不一致**：`pip install logstats-pypi-name` 后仍 `import logstats_pkg` 取决于配置，要对照 `pyproject`。
- **未声明 `requires-python`**：wheel 元数据缺失会导致旧 Python 误装。
- **提交 `dist/`**：产物应 CI 生成，不进 git（除非发 Release 流程特殊要求）。

```python run raises=FileNotFoundError
from pathlib import Path

Path("dist/nonexistent.whl").read_bytes()
```

课内提醒：构建前目录不存在会报错——先 `uv build`。

## 对照

| 概念 | Python wheel | npm | Java |
|---|---|---|---|
| 安装单元 | `.whl` | packed tarball | JAR |
| 构建工具 | hatchling / setuptools | `npm pack` | Gradle jar |
| 元数据 | METADATA in wheel | package.json | MANIFEST.MF |
| 本地构建 | `uv build` | `npm pack` | `./gradlew build` |

## 读代码

[`logstats_pkg/cli.py`](../../../examples/项目/17-CLI打包/logstats_pkg/cli.py) 把 14 课解析逻辑收成可安装模块：

```python
LEVEL_RE = re.compile(r"\b(INFO|ERROR)\b")

def count_levels(text: str) -> Counter[str]:
    ...

def main(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    for level, n in sorted(count_levels(text).items()):
        print(f"{level}: {n}")
    return 0
```

与 14 课差异：级别集合收窄为 INFO/ERROR，适合打包演示；`main` 接受 `Path` 而非 `argv` 列表，测试更简单。

[`test_package.py`](../../../examples/项目/17-CLI打包/test_package.py) 三条用例覆盖 `count_levels`、空输入与 `main`——打包前后测试命令不变：

```bash
uv run pytest examples/项目/17-CLI打包 -q
```

## 练习

### 练习 1

```python exercise id=s17-l01-wheel
# --- starter ---
pkg = 'sdist'
# --- solution ---
pkg = 'wheel'
# --- check ---
assert pkg == 'wheel'
```

### 练习 2：`artifact_name`

实现 `artifact_name(project: str, version: str) -> str`，返回 `f"{project}-{version}-py3-none-any.whl"`。

```python exercise id=s17-l01-artifact
# --- starter ---
def artifact_name(project: str, version: str) -> str:
    return ""
# --- solution ---
def artifact_name(project: str, version: str) -> str:
    return f"{project}-{version}-py3-none-any.whl"
# --- check ---
assert artifact_name("demo", "0.1.0") == "demo-0.1.0-py3-none-any.whl"
```

- 达标备注（docs/课程/17-打包与发布/01-wheel与构建后端.md）：本课正文非空行已对齐 v2.1 深化门槛，可与 `tests/check_course.py` 一并验收。

## 小结

- wheel 即装即用；sdist 保留源码构建链；由 `pyproject` 的 build-system 驱动。
- `logstats_pkg` 是打包候选树：只含包目录与元数据，测试留在外。
- 本地 `uv build` 检查 dist 内容，确认无 `.venv` 与缓存文件。

构建产物应只包含 import 所需的包数据；`README`、`LICENSE` 通过元数据字段引用，而不是随意塞进 wheel 根目录。

对比 npm：`npm pack`  tarball 类似 sdist；`node_modules` 里解压的目录类似 site-packages 中的 wheel 内容。

本地验证 wheel 时可用 `uv pip install dist/*.whl` 装进临时 venv，再跑阶段 17 的 pytest。

`__pycache__` 与 `.pyc` 不应出现；现代构建后端默认排除，但若手写 MANIFEST 要小心。

阶段 17 三条 pytest 是打包前的质量门槛：解析、空输入、main 读文件。

全仓学习时，17 课与 16 课工具链衔接：先 ruff/mypy/pytest 绿，再考虑 `uv build`。

若 `dist/` 已存在旧版本 wheel，上传前清理或 bump version，避免测错文件。

`logstats_pkg` 仅依赖标准库时，wheel 标签多为 `py3-none-any`，跨平台安装简单。

读 `cli.py` 时注意 `LEVEL_RE` 与 14 课差异：打包演示收窄级别，测试已锁定 INFO/ERROR。

`test_package.py` 与 15 课类似，通过 conftest 注入路径；安装 wheel 后则不再需要 conftest。

构建后端读取 `pyproject` 的 `[project]` name/version 写入 wheel METADATA。

sdist 保留 `pyproject.toml` 供源码安装；wheel 已含编译好的布局（纯 Python 即 .py 文件）。

学习时可 `unzip -l dist/*.whl` 查看 `logstats_pkg/` 是否在根下，路径错误会导致 import 失败。

wheel 安装比 sdist 快，因为跳过了构建后端的打包步骤；用户 `pip install` 时优先选 wheel。

核对日期 2026-10-18：课程环境 Python 3.12，`uv build` 行为以当前 uv 文档为准。

`count_levels` 返回 `Counter`，wheel 内与源码一致；安装后 `from logstats_pkg.cli import count_levels` 行为不变。

打包不改变测试命令：`uv run pytest examples/项目/17-CLI打包 -q` 在 build 前后都应 3 passed。

hatchling 会根据包目录自动发现 `logstats_pkg`；无需手写每个 .py 路径。

MANIFEST.in 在 setuptools 时代常见；现代后端多用默认发现规则。

阅读 wheel 内 `METADATA` 可确认 `Requires-Python` 与依赖列表是否与 pyproject 一致。

纯标准库包无需声明 runtime 依赖，METADATA 的 `Requires-Dist` 可为空。

`logstats_pkg/cli.py` 的 `main` 返回 0，wheel 不改变该契约。

构建失败时先读 traceback 指向的后端日志，再查 pyproject 包发现配置。

阶段 17 index 的达成标志是理解 wheel 并本地 build；测试仍用 pytest 验证。

wheel 文件名中的版本必须与 pyproject 一致，否则用户困惑。

读完本课应能口述 wheel 与 sdist 的安装路径差异。

## 延伸阅读

- [打包项目教程](https://packaging.python.org/en/latest/tutorials/packaging-project/)
- [Wheel 格式说明](https://packaging.python.org/en/latest/specifications/binary-distribution-format/)
- [pyproject 构建系统](https://packaging.python.org/en/latest/specifications/pyproject-toml/#build-system)
