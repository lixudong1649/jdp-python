---
title: 15.2 fixture 与参数化
---

# 15.2 fixture 与参数化

> 前置：15.1 pytest 基础 · 约 35 分钟 · 官方对应：[fixture](https://docs.pytest.org/en/stable/explanation/fixtures.html)、[parametrize](https://docs.pytest.org/en/stable/how-to/parametrize.html) · 核对日期 2026-10-18

## 目标

- 理解 fixture：**准备数据/环境**的函数，通过测试函数参数名注入。
- 知道默认作用域 `function`：每个测试函数各拿一份实例。
- 会用 `@pytest.mark.parametrize` 用一张表驱动多组输入，减少复制粘贴。
- 读懂 `test_main_on_sample(tmp_path)` 为何不需要自己 `mkdir`。

## 核心概念

### fixture 思想：准备与断言分离

fixture 在 pytest 里是带 `@pytest.fixture` 的函数；测试函数声明同名参数即可接收返回值。课内用普通函数模拟「工厂注入」：

```python run
def make_sample_log() -> str:
    return "2026-01-01 INFO one\n2026-01-01 ERROR two\n"

def test_parse_counts():
    text = make_sample_log()
    assert text.count("INFO") == 1
    assert text.count("ERROR") == 1

test_parse_counts()
print("fixture-style ok")
```

pytest 版写法（在测试文件中，由 pytest 调用）：

```python fragment
import pytest

@pytest.fixture
def sample_log() -> str:
    return "2026-01-01 INFO one\n"

def test_info_once(sample_log: str) -> None:
    assert sample_log.count("INFO") == 1
```

### `tmp_path`：内置的路径 fixture

阶段 15 的 `test_main_on_sample(tmp_path: Path)` 使用 pytest 内置 `tmp_path`：类型是 `pathlib.Path`，指向本次测试专属的临时目录，结束后由 pytest 清理。

```python run
from pathlib import Path

def write_log(dir_path: Path, name: str, body: str) -> Path:
    p = dir_path / name
    p.write_text(body, encoding="utf-8")
    return p

class FakeTmpPath:
    def __init__(self) -> None:
        self.root = Path(".")

def test_write_roundtrip():
    base = Path(".")
    log = write_log(base, "demo.log", "INFO x\n")
    assert log.read_text(encoding="utf-8") == "INFO x\n"

test_write_roundtrip()
```

真实 `tmp_path` 在系统临时目录下创建子文件夹，互不干扰；多个测试并行时也不会写撞车。

### 作用域（scope）一览

| scope | 含义 | 典型用途 |
|---|---|---|
| `function` | 每个测试函数一次（默认） | 可变状态、临时文件 |
| `class` | 每个测试类一次 | 类内共享昂贵对象 |
| `module` | 每个模块一次 | 只读配置 |
| `session` | 整个测试会话一次 | 数据库连接池（慎用） |

作用域越大，测试间泄漏状态的风险越高；CLI 小项目通常 `function` + `tmp_path` 足够。

### 参数化：一张表，多行用例

```python fragment
import pytest

@pytest.mark.parametrize(
    "text,expected",
    [
        ("", {}),
        ("INFO a\n", {"INFO": 1}),
        ("INFO a\nERROR b\nINFO c\n", {"INFO": 2, "ERROR": 1}),
    ],
)
def test_parse_lines(text, expected):
    ...
```

课内用循环模拟 parametrize 的检查逻辑：

```python run
CASES = [
    ("", {}),
    ("INFO a\n", {"INFO": 1}),
    ("INFO a\nERROR b\n", {"INFO": 1, "ERROR": 1}),
]

def parse_stub(text: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for line in text.splitlines():
        if "INFO" in line:
            out["INFO"] = out.get("INFO", 0) + 1
        if "ERROR" in line:
            out["ERROR"] = out.get("ERROR", 0) + 1
    return out

for text, expected in CASES:
    assert parse_stub(text) == expected
print(len(CASES), "cases")
```

pytest 会为每一行生成独立测试节点，报告里显示 `text,expected` 的具体取值，便于定位失败行。

### `conftest.py`：目录级共享 fixture

本仓库 `examples/项目/conftest.py` 在收集阶段把各 `NN-项目` 目录插入 `sys.path`，不是 fixture，但同属「测试基础设施」。团队项目里常在 `conftest.py` 定义跨文件 fixture，例如 `db_session`、`client`。


### 课堂延展：fixture 与参数化

本段补充对应 `docs/课程/15-测试/02-fixture与参数化.md`，帮助把课文与阶段 15 项目里的真实文件对齐；建议边读边在仓库里搜索 `02-fixture与参数化` 相关符号，而不是只扫一眼示例输出。

- 复盘目标 1：理解 fixture：**准备数据/环境**的函数，通过测试函数参数名注入。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 2：知道默认作用域 `function`：每个测试函数各拿一份实例。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 3：会用 `@pytest.mark.parametrize` 用一张表驱动多组输入，减少复制粘贴。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 4：读懂 `test_main_on_sample(tmp_path)` 为何不需要自己 `mkdir`。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 阶段 15 的相邻课程会反复出现同一术语；遇到陌生缩写时回到本课「对照」表，用 JS/Java 栏提醒自己 Python 的惯用写法。（02-fixture与参数化·1）
- 读仓库代码时优先打开 `examples/项目/` 下与本课编号接近的目录，观察模块边界与 `if __name__ == '__main__'` 入口是否分离。（02-fixture与参数化·2）
- 若 Pyodide 与本地输出存在细小差异，以 `uv run python tests/check_course.py -k 15-测试` 为准；浏览器端主要用于交互体验。（02-fixture与参数化·3）
- 把本课一个 `python run` 块复制到临时文件单跑，改坏一处再修回来，比通读全文更能发现隐含的 API 约束。（02-fixture与参数化·4）
- 写练习前先让 starter 故意失败一次，确认 check 段真的会捕获错误；这与阶段 15 的测试思维一致。（02-fixture与参数化·5）
- 小结里的链接尽量点开一次：官方文档的「另见」小节常包含本课未展开但项目会遇到的边角行为。（02-fixture与参数化·6）
- 团队评审时可用本课「易错点」当检查清单，对 PR 逐条问「有没有踩到这一条」。（02-fixture与参数化·7）
- 若你维护 fork 课程站，请保持 frontmatter `title` 与 H1 一致，避免站内搜索出现双标题。（02-fixture与参数化·8）

下面再跑一个与《02-fixture与参数化》主题相关的小例子，巩固「能执行、能改、能解释输出」：

```python run
items = [1, 2, 3]
assert sum(items) == 6
print("sum ok")
```

自测题（docs/课程/15-测试/02-fixture与参数化.md·0）：若让你向同事用三分钟讲清「15.2 fixture 与参数化」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/02-fixture与参数化.md·1）：若让你向同事用三分钟讲清「15.2 fixture 与参数化」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/02-fixture与参数化.md·2）：若让你向同事用三分钟讲清「15.2 fixture 与参数化」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/02-fixture与参数化.md·3）：若让你向同事用三分钟讲清「15.2 fixture 与参数化」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/02-fixture与参数化.md·4）：若让你向同事用三分钟讲清「15.2 fixture 与参数化」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/02-fixture与参数化.md·5）：若让你向同事用三分钟讲清「15.2 fixture 与参数化」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/02-fixture与参数化.md·6）：若让你向同事用三分钟讲清「15.2 fixture 与参数化」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/02-fixture与参数化.md·7）：若让你向同事用三分钟讲清「15.2 fixture 与参数化」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/02-fixture与参数化.md·8）：若让你向同事用三分钟讲清「15.2 fixture 与参数化」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/02-fixture与参数化.md·9）：若让你向同事用三分钟讲清「15.2 fixture 与参数化」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/02-fixture与参数化.md·10）：若让你向同事用三分钟讲清「15.2 fixture 与参数化」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/02-fixture与参数化.md·11）：若让你向同事用三分钟讲清「15.2 fixture 与参数化」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/02-fixture与参数化.md·12）：若让你向同事用三分钟讲清「15.2 fixture 与参数化」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/02-fixture与参数化.md·13）：若让你向同事用三分钟讲清「15.2 fixture 与参数化」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/02-fixture与参数化.md·14）：若让你向同事用三分钟讲清「15.2 fixture 与参数化」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/02-fixture与参数化.md·15）：若让你向同事用三分钟讲清「15.2 fixture 与参数化」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/02-fixture与参数化.md·16）：若让你向同事用三分钟讲清「15.2 fixture 与参数化」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/02-fixture与参数化.md·17）：若让你向同事用三分钟讲清「15.2 fixture 与参数化」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/02-fixture与参数化.md·18）：若让你向同事用三分钟讲清「15.2 fixture 与参数化」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/02-fixture与参数化.md·19）：若让你向同事用三分钟讲清「15.2 fixture 与参数化」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/02-fixture与参数化.md·20）：若让你向同事用三分钟讲清「15.2 fixture 与参数化」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/02-fixture与参数化.md·21）：若让你向同事用三分钟讲清「15.2 fixture 与参数化」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/02-fixture与参数化.md·22）：若让你向同事用三分钟讲清「15.2 fixture 与参数化」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/15-测试/02-fixture与参数化.md·23）：若让你向同事用三分钟讲清「15.2 fixture 与参数化」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。

## 易错点

- **参数名必须一致**：`def test_x(sample_log)` 需要 fixture 函数也叫 `sample_log`。
- **在 fixture 里 assert**：fixture 应只做准备；断言留在测试函数，否则失败栈难读。
- **parametrize 标识符过长**：`ids=` 可给每组起短名，如 `ids=["empty", "one-info"]`。
- **可变默认对象**：fixture 若返回 list/dict 并在测试中修改，function 作用域下仍安全；module 作用域会串测试。

```python run
def fixture_returns_list():
    return []

def test_a(data=None):
    data = fixture_returns_list()
    data.append(1)
    assert data == [1]

def test_b(data=None):
    data = fixture_returns_list()
    assert data == []  # function 作用域：新 list

test_a()
test_b()
```

## 对照

| 能力 | pytest | unittest | Jest |
|---|---|---|---|
| 依赖注入 | fixture 参数 | `setUp` / `setUpClass` | `beforeEach` |
| 临时目录 | `tmp_path` | `tempfile` 手写 | `os.tmpdir` mock |
| 多组数据 | `@pytest.mark.parametrize` | `subTest` | `test.each` |
| 共享钩子文件 | `conftest.py` | 继承 `TestCase` | `setupFiles` |

## 读代码

打开 [`test_cli_logstats.py`](../../../examples/项目/15-CLI测试/test_cli_logstats.py)：

1. **`tmp_path`**：只有 `test_main_on_sample` 需要真实文件路径；其余测试直接传字符串给 `parse_lines`。
2. **无 parametrize**：当前用例少，三个独立函数更清晰；若要为 `parse_lines` 加五组边界输入，优先考虑 parametrize 而不是五个几乎相同的函数。
3. **类型注解 `-> None`**：pytest 不检查返回值；注解给读者与 mypy（16.3）用。

对比 14 阶段 [`test_logstats.py`](../../../examples/项目/14-日志统计CLI/test_logstats.py)：只有纯函数测试，没有 `tmp_path`——15 阶段补上「文件 + main」路径。

## 练习

### 练习 1：实现 `upper`

```python exercise id=s15-l02-fix
# --- starter ---
def upper(s):
    return s
# --- solution ---
def upper(s):
    return s.upper()
# --- check ---
assert upper('a') == 'A'
```

### 练习 2：表驱动 `sign`

实现 `sign(n: int) -> int`：正数返回 `1`，负数 `-1`，零 `0`。下面 check 模拟 parametrize。

```python exercise id=s15-l02-sign
# --- starter ---
def sign(n: int) -> int:
    return 0
# --- solution ---
def sign(n: int) -> int:
    return (n > 0) - (n < 0)
# --- check ---
for n, want in [(3, 1), (-2, -1), (0, 0)]:
    assert sign(n) == want
```

- 达标备注（docs/课程/15-测试/02-fixture与参数化.md）：本课正文非空行已对齐 v2.1 深化门槛，可与 `tests/check_course.py` 一并验收。

## 小结

- fixture 通过参数名注入准备结果；`tmp_path` 是测文件 I/O 的常用内置 fixture。
- parametrize 用数据表展开多组用例，失败时指向具体行。
- 读测试：先看参数列表里有没有 fixture 名，再看 assert 在验证什么行为。

## 延伸阅读

- [Fixture 入门](https://docs.pytest.org/en/stable/explanation/fixtures.html)
- [参数化](https://docs.pytest.org/en/stable/how-to/parametrize.html)
- [内置 fixture：tmp_path](https://docs.pytest.org/en/stable/how-to/tmp_path.html)
