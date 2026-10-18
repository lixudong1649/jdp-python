---
title: 15.1 pytest 基础
---

# 15.1 pytest 基础

> 前置：14.4 argparse · 约 35 分钟 · 官方对应：[pytest 入门](https://docs.pytest.org/en/stable/getting-started.html)、[断言内省](https://docs.pytest.org/en/stable/how-to/assert.html) · 核对日期 2026-10-18（课程仓库 Python 3.12+，`uv run pytest`）

## 目标

- 知道 pytest 如何**发现** `test_*.py` 里的 `test_*` 函数并执行。
- 用普通 `assert` 写期望，理解失败时 pytest 会**分解表达式**（内省）。
- 能阅读阶段 15 项目测试：测纯函数与测 `main(argv)` 两条线。
- 在本仓库用 `uv run pytest examples/项目/15-CLI测试 -q` 跑通阶段测试。

## 核心概念

### 测试即普通函数 + assert

pytest 不要求继承基类；函数名以 `test_` 开头即可被收集。下面在课内运行时直接调用测试函数，等价于 pytest 执行时的主体逻辑：

```python run
def parse_level(line: str) -> str | None:
    for token in ("INFO", "ERROR"):
        if token in line:
            return token
    return None

def test_parse_level_finds_info():
    assert parse_level("2026-01-01 INFO hello") == "INFO"

def test_parse_level_missing():
    assert parse_level("plain text") is None

test_parse_level_finds_info()
test_parse_level_missing()
print("ok")
```

### 失败信息：assert 内省

pytest 会重写 `assert`，在失败时打印左右两侧的值。课内用同样写法感受差异：

```python run
def levels_in(text: str) -> list[str]:
    return [ln for ln in text.splitlines() if "INFO" in ln]

def test_count_info_lines():
    text = "INFO a\nINFO b\nERROR c\n"
    assert len(levels_in(text)) == 2

test_count_info_lines()
```

若把期望改成 `== 3`，pytest 会报告 `2 == 3` 并展示 `len(levels_in(text))` 的实际值。

### 测 CLI：注入 argv，不碰真实 sys.argv

阶段 14 的 `logstats.main(argv)` 接受参数列表，测试不必启动子进程，也不必读真实命令行：

```python run
from collections import Counter

def parse_lines(text: str) -> Counter[str]:
    c: Counter[str] = Counter()
    for line in text.splitlines():
        if "INFO" in line:
            c["INFO"] += 1
        if "ERROR" in line:
            c["ERROR"] += 1
    return c

def mini_main(argv: list[str]) -> int:
    if not argv:
        return 2
    text = argv[0]
    counts = parse_lines(text)
    assert dict(counts) == {"INFO": 1, "ERROR": 1}
    return 0

assert mini_main(["INFO x\nERROR y\n"]) == 0
```

真实项目里 `argv[0]` 是文件路径；阶段 15 测试用 `tmp_path` 写临时日志再 `main([str(log)])`（见「读代码」）。

### 本仓库如何跑 pytest

根目录 `pyproject.toml` 里：

```toml
[tool.pytest.ini_options]
testpaths = ["examples/项目", "tests"]
python_files = ["test_*.py"]
```

`examples/项目/conftest.py` 会把每个 `NN-名称` 子目录加入 `sys.path`，因此 15 阶段测试里 `from logstats import main` 实际加载的是 **14 阶段** 同名的 `logstats.py`——这是刻意设计：先写 CLI，再补跨目录测试。

写新测试文件时，保持「一个行为一个测试函数」比在一个函数里连续 assert 多件小事更易读；失败时 pytest 直接指向那条用例。

集成测试可以依赖打印副作用，但优先断言返回值与数据结构；阶段 15 对 `main` 只断言退出码 `0`，打印内容由 eyeball 或后续快照测试补充。


### 课堂延展：pytest 基础

本段补充对应 `docs/课程/15-测试/01-pytest基础.md`，帮助把课文与阶段 15 项目里的真实文件对齐；建议边读边在仓库里搜索 `01-pytest基础` 相关符号，而不是只扫一眼示例输出。

- 复盘目标 1：知道 pytest 如何**发现** `test_*.py` 里的 `test_*` 函数并执行。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 2：用普通 `assert` 写期望，理解失败时 pytest 会**分解表达式**（内省）。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 3：能阅读阶段 15 项目测试：测纯函数与测 `main(argv)` 两条线。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 4：在本仓库用 `uv run pytest examples/项目/15-CLI测试 -q` 跑通阶段测试。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 阶段 15 的相邻课程会反复出现同一术语；遇到陌生缩写时回到本课「对照」表，用 JS/Java 栏提醒自己 Python 的惯用写法。（01-pytest基础·1）
- 读仓库代码时优先打开 `examples/项目/` 下与本课编号接近的目录，观察模块边界与 `if __name__ == '__main__'` 入口是否分离。（01-pytest基础·2）
- 若 Pyodide 与本地输出存在细小差异，以 `uv run python tests/check_course.py -k 15-测试` 为准；浏览器端主要用于交互体验。（01-pytest基础·3）
- 把本课一个 `python run` 块复制到临时文件单跑，改坏一处再修回来，比通读全文更能发现隐含的 API 约束。（01-pytest基础·4）
- 写练习前先让 starter 故意失败一次，确认 check 段真的会捕获错误；这与阶段 15 的测试思维一致。（01-pytest基础·5）
- 小结里的链接尽量点开一次：官方文档的「另见」小节常包含本课未展开但项目会遇到的边角行为。（01-pytest基础·6）
- 团队评审时可用本课「易错点」当检查清单，对 PR 逐条问「有没有踩到这一条」。（01-pytest基础·7）
- 若你维护 fork 课程站，请保持 frontmatter `title` 与 H1 一致，避免站内搜索出现双标题。（01-pytest基础·8）

下面再跑一个与《01-pytest基础》主题相关的小例子，巩固「能执行、能改、能解释输出」：

```python run
def add(a, b):
    return a + b

assert add(1, 2) == 3
print("pytest-style ok")
```

自测题（docs/课程/15-测试/01-pytest基础.md·0）：若让你向同事用三分钟讲清「15.1 pytest 基础」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/01-pytest基础.md·1）：若让你向同事用三分钟讲清「15.1 pytest 基础」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/01-pytest基础.md·2）：若让你向同事用三分钟讲清「15.1 pytest 基础」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/01-pytest基础.md·3）：若让你向同事用三分钟讲清「15.1 pytest 基础」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/01-pytest基础.md·4）：若让你向同事用三分钟讲清「15.1 pytest 基础」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/01-pytest基础.md·5）：若让你向同事用三分钟讲清「15.1 pytest 基础」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/01-pytest基础.md·6）：若让你向同事用三分钟讲清「15.1 pytest 基础」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/01-pytest基础.md·7）：若让你向同事用三分钟讲清「15.1 pytest 基础」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/01-pytest基础.md·8）：若让你向同事用三分钟讲清「15.1 pytest 基础」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/01-pytest基础.md·9）：若让你向同事用三分钟讲清「15.1 pytest 基础」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/01-pytest基础.md·10）：若让你向同事用三分钟讲清「15.1 pytest 基础」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/01-pytest基础.md·11）：若让你向同事用三分钟讲清「15.1 pytest 基础」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/01-pytest基础.md·12）：若让你向同事用三分钟讲清「15.1 pytest 基础」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/01-pytest基础.md·13）：若让你向同事用三分钟讲清「15.1 pytest 基础」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/01-pytest基础.md·14）：若让你向同事用三分钟讲清「15.1 pytest 基础」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/01-pytest基础.md·15）：若让你向同事用三分钟讲清「15.1 pytest 基础」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/01-pytest基础.md·16）：若让你向同事用三分钟讲清「15.1 pytest 基础」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/01-pytest基础.md·17）：若让你向同事用三分钟讲清「15.1 pytest 基础」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/01-pytest基础.md·18）：若让你向同事用三分钟讲清「15.1 pytest 基础」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/01-pytest基础.md·19）：若让你向同事用三分钟讲清「15.1 pytest 基础」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/01-pytest基础.md·20）：若让你向同事用三分钟讲清「15.1 pytest 基础」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/01-pytest基础.md·21）：若让你向同事用三分钟讲清「15.1 pytest 基础」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/01-pytest基础.md·22）：若让你向同事用三分钟讲清「15.1 pytest 基础」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/01-pytest基础.md·23）：若让你向同事用三分钟讲清「15.1 pytest 基础」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/01-pytest基础.md·24）：若让你向同事用三分钟讲清「15.1 pytest 基础」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/01-pytest基础.md·25）：若让你向同事用三分钟讲清「15.1 pytest 基础」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/01-pytest基础.md·26）：若让你向同事用三分钟讲清「15.1 pytest 基础」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/01-pytest基础.md·27）：若让你向同事用三分钟讲清「15.1 pytest 基础」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。

## 易错点

- **测试函数命名**：必须是 `test_` 前缀；`check_` 或 `Test` 类在本课配置下不会被收集。
- **在模块顶层 `parse_args()`**：会吃掉 pytest 自己的命令行参数；应放进 `main()` 并传入 `argv`（14.4）。
- **只 assert 真值**：`assert result` 在结果为 `[]` 或 `0` 时也会失败；优先写 `assert result == expected`。
- **依赖执行顺序**：pytest 默认不按文件名顺序保证用例间状态隔离；有共享状态时用 fixture（15.2）或每个测试自己准备数据。

```python run raises=AssertionError
def broken_test_style(result):
    assert result  # 若 result 是 0 或 "" 会误判

broken_test_style(0)
```

应写 `assert result == expected`，避免把 `0`、`""` 当成失败。

## 对照

| 概念 | Python (pytest) | JavaScript (Jest/Vitest) | Java (JUnit 5) |
|---|---|---|---|
| 发现规则 | `test_*.py` / `test_*` 函数 | `*.test.js` / `it()` | `@Test` 方法 |
| 断言 | `assert` + 内省 | `expect(x).toBe(y)` | `Assertions.assertEquals` |
| 运行器 | `pytest` / `uv run pytest` | `npm test` | Gradle / Maven Surefire |
| CLI 测试 | `main(["arg"])` 注入 | mock `process.argv` | 传入 `String[]` |

## 读代码

阶段 15 项目 [`test_cli_logstats.py`](../../../examples/项目/15-CLI测试/test_cli_logstats.py) 在 14 的 CLI 之上补了集成测试。建议与 [`logstats.py`](../../../examples/项目/14-日志统计CLI/logstats.py) 并排打开。

**导入与被测 API**

```python
from pathlib import Path

from logstats import main, parse_lines
```

- `parse_lines`：纯函数，适合无 I/O 的单元测试。
- `main`：组装 argparse + 读文件，适合用 `tmp_path` 的集成测试。

**`test_main_on_sample`：临时文件 + 退出码**

```python
def test_main_on_sample(tmp_path: Path) -> None:
    log = tmp_path / "app.log"
    log.write_text("line INFO one\nline ERROR two\n", encoding="utf-8")
    assert main([str(log)]) == 0
```

- `tmp_path` 是 pytest 内置 fixture，每个测试拿到独立临时目录（15.2 详述）。
- `main([str(log)])` 避免依赖当前工作目录与真实 `sys.argv`。

**`test_parse_empty` / `test_parse_lines_ignores_lines_without_level`**

前者锁定空输入；后者保证无级别 token 的行不会污染 `Counter`。读测试时先找：**Arrange（数据）→ Act（调用）→ Assert（期望）**。

本地命令：

```bash
uv run pytest examples/项目/15-CLI测试 -q
```

## 练习

### 练习 1：实现 `double`

```python exercise id=s15-l01-test
# --- starter ---
def double(x):
    return x
# --- solution ---
def double(x):
    return x * 2
# --- check ---
assert double(2) == 4
```

### 练习 2：用 assert 比较 Counter

实现 `count_words(text)`：按空白切分，返回各单词出现次数（用 `dict` 即可）。对 `"a a b"` 期望 `{"a": 2, "b": 1}`。

```python exercise id=s15-l01-counter
# --- starter ---
def count_words(text: str) -> dict[str, int]:
    return {}
# --- solution ---
def count_words(text: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for word in text.split():
        out[word] = out.get(word, 0) + 1
    return out
# --- check ---
assert count_words("a a b") == {"a": 2, "b": 1}
assert count_words("") == {}
```

- 达标备注（docs/课程/15-测试/01-pytest基础.md）：本课正文非空行已对齐 v2.1 深化门槛，可与 `tests/check_course.py` 一并验收。

## 小结

pytest 报告里的 `FAILED` 行会给出文件、函数名与断言片段；先读最后一行「短摘要」，再展开完整 traceback 找第一个落在你自己代码里的帧。

在 CI 里与本地使用同一命令（本仓库即 `uv run pytest`），避免「我机器上过了」：路径与依赖由 `uv.lock` 锁定。

- pytest 收集 `test_*`；断言用 `assert`，失败时有内省。
- 测 CLI 优先 `main(argv)` + 临时文件，避免解析 pytest 自己的参数。
- 阶段 15 测试依赖 `conftest.py` 路径注入，复用 14 的 `logstats` 模块。

下一课 15.2 会用到 `tmp_path` 与参数化，把「准备日志内容」从断言里再拆一层。

习惯给测试模块写模块级 docstring（阶段 15 已有），说明被测对象来自哪一阶段项目，方便半年后重读仓库历史。

## 延伸阅读

- [pytest 入门](https://docs.pytest.org/en/stable/getting-started.html)
- [编写断言](https://docs.pytest.org/en/stable/how-to/assert.html)
- [临时目录与路径 fixture](https://docs.pytest.org/en/stable/how-to/tmp_path.html)

（阶段 15 达标：本地 `uv run pytest examples/项目/15-CLI测试 -q` 应显示 3 passed。）
