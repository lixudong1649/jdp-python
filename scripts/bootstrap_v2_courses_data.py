"""阶段 13–24 课程数据（由 bootstrap_v2_courses.py 消费）。"""
from __future__ import annotations

EXTRA_STAGES: list[dict] = []


def _lesson(
    slug: str,
    title: str,
    prereq: str,
    official: str,
    goals: list[str],
    concept: str,
    pitfalls: str,
    read_code: str,
    ex_id: str,
    starter: str,
    solution: str,
    check: str,
    summary: list[str],
    links: list[str],
    *,
    pitfall_run: str = "",
) -> dict:
    compare = "| 概念 | Python | JS | Java |\n|---|---|---|---|\n| 本节重点 | 见官方文档 | — | — |"
    return {
        "slug": slug,
        "title": title,
        "prereq": prereq,
        "official": official,
        "goals": goals,
        "concept": concept,
        "pitfalls": pitfalls,
        "compare": compare,
        "read_code": read_code,
        "ex_id": ex_id,
        "starter": starter,
        "solution": solution,
        "check": check,
        "summary": summary,
        "links": links,
        "pitfall_run": pitfall_run,
    }


def _stage(
    no: int,
    slug: str,
    short: str,
    layer: str,
    goal: str,
    project: str,
    lessons: list[dict],
) -> None:
    EXTRA_STAGES.append(
        {"no": no, "slug": slug, "short": short, "layer": layer, "goal": goal, "project": project, "lessons": lessons}
    )


_stage(
    13,
    "13-函数式与进阶语法",
    "函数式与进阶语法",
    "L2",
    "能写装饰器与上下文管理器",
    "examples/项目/13-计时重试装饰器/timing.py",
    [
        _lesson(
            "01-functools入门",
            "functools 入门",
            "10.2 装饰器",
            "[functools](https://docs.python.org/zh-cn/3/library/functools.html)",
            ["会用 partial 固定参数", "会用 lru_cache 做纯函数缓存", "会用 wraps 保留元信息"],
            """```python run
import functools

@functools.lru_cache(maxsize=32)
def fib(n: int) -> int:
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

print(fib(10), fib.cache_info().hits)
```""",
            "- `lru_cache` 要求参数可哈希。\n- 忘记 `@wraps` 导致 `help(fn)` 显示 wrapper。",
            "读装饰器源码时常见 `functools.wraps`；SDK 中间层也会缓存只读查询。",
            "s13-l01-partial",
            "import functools\n\ndef mul(a, b):\n    return a * b",
            "import functools\n\ndef mul(a, b):\n    return a * b\n\ndouble = functools.partial(mul, 2)",
            "assert double(5) == 10",
            ["partial 预先绑定参数", "lru_cache 适合昂贵纯函数"],
            ["[functools](https://docs.python.org/zh-cn/3/library/functools.html)"],
        ),
        _lesson(
            "02-带参装饰器",
            "带参装饰器",
            "10.2 装饰器",
            "[函数定义](https://docs.python.org/zh-cn/3/reference/compound_stmts.html#function-definitions)",
            ["写出三层嵌套的带参装饰器", "理解 `@deco(arg)` 的两次调用"],
            """```python run
import functools

def repeat(times: int):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            out = None
            for _ in range(times):
                out = func(*args, **kwargs)
            return out
        return wrapper
    return deco

@repeat(2)
def greet(name: str) -> str:
    return f"hi {name}"

print(greet("py"))
```""",
            "- 少一层嵌套会把装饰器参数当成被装饰函数。\n- 多个装饰器从下往上包裹。",
            "框架里 `@app.get(\"/path\")` 就是带参装饰器；先读外层参数含义。",
            "s13-l02-deco",
            "def tag(name):\n    def deco(func):\n        return func\n    return deco",
            "def tag(name):\n    def deco(func):\n        def wrapper():\n            return f\"<{name}>\" + func() + f\"</{name}>\"\n        return wrapper\n    return deco\n\n@tag(\"b\")\ndef hi():\n    return \"x\"",
            'assert hi() == "<b>x</b>"',
            ["带参装饰器先调用外层", "内层才是 classic decorator"],
            ["[术语：装饰器](https://docs.python.org/zh-cn/3/glossary.html#term-decorator)"],
        ),
        _lesson(
            "03-contextlib上下文管理器",
            "contextlib 上下文管理器",
            "6.3 with 与上下文管理器",
            "[contextlib](https://docs.python.org/zh-cn/3/library/contextlib.html)",
            ["用 `@contextmanager` 写 with 块", "理解 yield 前后是 setup/teardown"],
            """```python run
from contextlib import contextmanager

@contextmanager
def opened(path: str):
    f = open(path, "w", encoding="utf-8")
    try:
        yield f
    finally:
        f.close()

with opened("/tmp/ctx-demo.txt") as f:
    f.write("ok")
print("done")
```""",
            "- `yield` 只能出现一次。\n- 忘记 finally 会导致资源泄漏。",
            "`with client:` 或 SDK 提供的上下文管理器，读 `__enter__/__exit__` 或 `@contextmanager`。",
            "s13-l03-ctx",
            "from contextlib import contextmanager\n\n@contextmanager\ndef tag(name):\n    yield name",
            "from contextlib import contextmanager\n\n@contextmanager\ndef tag(name):\n    yield name\n\nwith tag('x') as v:\n    got = v",
            "assert got == 'x'",
            ["contextmanager 生成器变 with", "finally 保证清理"],
            ["[contextlib](https://docs.python.org/zh-cn/3/library/contextlib.html)"],
        ),
        _lesson(
            "04-match语句",
            "match 语句",
            "3.1 条件与循环",
            "[match 语句](https://docs.python.org/zh-cn/3/reference/compound_stmts.html#the-match-statement)（3.10 起）",
            ["用 match/case 做结构化分支", "结合序列模式与字面量"],
            """```python run
def kind(x):
    match x:
        case {"type": "text", "text": t}:
            return f"text:{t}"
        case {"type": name}:
            return f"other:{name}"
        case _:
            return "unknown"

print(kind({"type": "text", "text": "hi"}))
```""",
            "- case 顺序从上到下匹配。\n- 不要用 match 替代简单 if 导致可读性下降。",
            "读消息块时可 match `block.type`；与 if/elif 等价但模式更清晰。",
            "s13-l04-match",
            "def label(x):\n    return 'x'",
            "def label(x):\n    match x:\n        case 1:\n            return 'one'\n        case _:\n            return 'other'",
            "assert label(1) == 'one' and label(2) == 'other'",
            ["match 3.10 起可用", "模式可解构 dict"],
            ["[match 语句](https://docs.python.org/zh-cn/3/reference/compound_stmts.html#the-match-statement)"],
        ),
    ],
)

_stage(
    14,
    "14-文本文件与命令行",
    "文本、文件与命令行",
    "L2",
    "能写带 argparse 的 CLI 工具",
    "examples/项目/14-日志统计CLI/logstats.py",
    [
        _lesson(
            "01-编码与bytes",
            "编码与 bytes",
            "2.3 字符串",
            "[二进制数据](https://docs.python.org/zh-cn/3/library/stdtypes.html#binary-sequence-types-bytes-bytearray-memoryview)",
            ["区分 str 与 bytes", "会用 encode/decode 指定 UTF-8"],
            """```python run
text = "上海"
b = text.encode("utf-8")
print(b, b.decode("utf-8"))
```""",
            "- 文本文件用 str，二进制用 bytes。\n- 默认 UTF-8，但 Windows 历史编码可能不同。",
            "HTTP/SDK 载荷常在 JSON（str）与 bytes 间转换；读 `content-type` 判断。",
            "s14-l01-bytes",
            "s = 'a'",
            "s = 'a'\nb = s.encode('utf-8')",
            "assert b == b'a'",
            ["bytes 是二进制序列", "str.encode 与 bytes.decode 成对"],
            ["[Unicode HOWTO](https://docs.python.org/zh-cn/3/howto/unicode.html)"],
        ),
        _lesson(
            "02-re正则",
            "re 正则",
            "8. 常用标准库",
            "[re 模块](https://docs.python.org/zh-cn/3/library/re.html)",
            ["会用 search/findall", "知道原始字符串 r\"...\""],
            """```python run
import re
m = re.search(r"\\d+", "temp=22C")
print(m.group(0) if m else None)
```""",
            "- 贪婪匹配导致过多捕获。\n- 复杂正则难维护，优先 str 方法。",
            "日志解析、路径提取会见到 re；先读模式字符串再读 group。",
            "s14-l02-re",
            "import re\n\nm = re.search('z', 'cat')",
            "import re\n\nm = re.search('a', 'cat')",
            "assert m and m.group(0) == 'a'",
            ["原始字符串减少转义", "search 找首个匹配"],
            ["[re](https://docs.python.org/zh-cn/3/library/re.html)"],
        ),
        _lesson(
            "03-csv与tomllib",
            "csv 与 tomllib",
            "4.2 字典",
            "[csv](https://docs.python.org/zh-cn/3/library/csv.html)",
            ["用 csv 模块读写表格", "知道 tomllib 读 pyproject（3.11 起标准库）"],
            """```python run
import csv
from io import StringIO
buf = StringIO("a,b\\n1,2\\n")
rows = list(csv.reader(buf))
print(rows)
```""",
            "- 未指定 newline='' 时 csv 可能行为异常。\n- TOML 不是 JSON，字段规则不同。",
            "配置文件 pyproject.toml 用 TOML；读工具链文档时对照 tomllib 解析结果。",
            "s14-l03-csv",
            "row = ['y']",
            "import csv\nfrom io import StringIO\nbuf = StringIO('x\\n1\\n')\nrow = next(csv.reader(buf))",
            "assert row == ['x']",
            ["csv 处理行与分隔符", "tomllib 只读（3.11+）"],
            [
                "[csv](https://docs.python.org/zh-cn/3/library/csv.html)",
                "[tomllib](https://docs.python.org/zh-cn/3/library/tomllib.html)",
            ],
        ),
        _lesson(
            "04-argparse",
            "argparse",
            "3.2 函数",
            "[argparse](https://docs.python.org/zh-cn/3/library/argparse.html)",
            ["定义位置参数与可选 flag", "在 main 中 parse 并返回 exit code"],
            """```python run
import argparse

p = argparse.ArgumentParser()
p.add_argument("name")
args = p.parse_args(["Ada"])
print(args.name)
```""",
            "- `parse_args()` 在无 argv 时会读 sys.argv。\n- 子命令用 add_subparsers。",
            "CLI 工具入口通常是 `if __name__ == '__main__'` + argparse；先找 subcommand。",
            "s14-l04-arg",
            "import argparse\n\np = argparse.ArgumentParser()\np.add_argument('x')",
            "import argparse\n\np = argparse.ArgumentParser()\np.add_argument('x')\nargs = p.parse_args(['3'])",
            "assert args.x == '3'",
            ["argparse 生成帮助信息", "适合可安装脚本 CLI"],
            ["[argparse 教程](https://docs.python.org/zh-cn/3/howto/argparse.html)"],
        ),
    ],
)

# Stage 15–24: lessons with static third-party mentions + pyodide-safe run blocks
_stage(
    15,
    "15-测试",
    "测试",
    "L3",
    "给项目写 pytest 测试并跑通",
    "examples/项目/15-CLI测试/test_cli_logstats.py",
    [
        _lesson(
            "01-pytest基础",
            "pytest 基础",
            "14.4 argparse",
            "[pytest 文档](https://docs.pytest.org/en/stable/)",
            ["写 test_ 函数与 assert", "用 uv run pytest 收集测试"],
            """```python run
def add(a, b):
    return a + b

def test_add():
    assert add(1, 2) == 3
```""",
            "- 测试函数必须以 test_ 开头。\n- assert 失败会给出表达式分解（pytest 特性）。",
            "项目测试在 `examples/项目/15-CLI测试/`；本地命令：`uv run pytest examples/项目/15-CLI测试 -q`。",
            "s15-l01-test",
            "def double(x):\n    return x",
            "def double(x):\n    return x * 2",
            "assert double(2) == 4",
            ["pytest 发现 test_*", "assert 即期望"],
            ["[pytest 入门](https://docs.pytest.org/en/stable/getting-started.html)"],
        ),
        _lesson(
            "02-fixture与参数化",
            "fixture 与参数化",
            "15.1 pytest 基础",
            "[fixture](https://docs.pytest.org/en/stable/explanation/fixtures.html)",
            ["理解 fixture 注入", "知道 @pytest.mark.parametrize 多组输入"],
            """```python run
def sample():
    return [1, 2, 3]

def test_len():
    assert len(sample()) == 3
```""",
            "- fixture 作用域默认 function。\n- parametrize 测试名会变长，注意可读性。",
            " conftest.py 里共享 fixture；读测试先看参数名对应哪个 fixture。",
            "s15-l02-fix",
            "def upper(s):\n    return s",
            "def upper(s):\n    return s.upper()",
            "assert upper('a') == 'A'",
            ["fixture 提供准备数据", "parametrize 减少重复用例"],
            ["[fixtures](https://docs.pytest.org/en/stable/explanation/fixtures.html)"],
        ),
        _lesson(
            "03-mock",
            "mock 与 monkeypatch",
            "15.2 fixture",
            "[monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)",
            ["用 monkeypatch 替换环境变量或函数", "避免真实网络调用"],
            """```python run
import os

def provider():
    return os.getenv("LLM_PROVIDER", "default")

os.environ["LLM_PROVIDER"] = "demo"
assert provider() == "demo"
```""",
            "- mock 过多导致测试与实现耦合。\n- 记得恢复环境，pytest monkeypatch 会自动恢复。",
            "测 Agent 时用 fake client 替代 SDK；与 minimal_agent 的 PROVIDERS 思路一致。",
            "s15-l03-mock",
            "def always_true():\n    return False",
            "def always_true():\n    return True",
            "assert always_true()",
            ["隔离外部依赖", "monkeypatch 改 os.environ"],
            ["[monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)"],
        ),
        _lesson(
            "04-覆盖率",
            "覆盖率概念",
            "15.1 pytest 基础",
            "[pytest-cov 说明](https://docs.pytest.org/en/stable/)",
            ["知道覆盖率是信号不是 KPI", "优先覆盖分支与错误路径"],
            """```python run
def safe_div(a, b):
    if b == 0:
        raise ValueError("zero")
    return a / b

try:
    safe_div(1, 0)
except ValueError:
    pass
else:
    raise AssertionError
```""",
            "- 100% 覆盖率仍可能漏测语义。\n- 不要为覆盖率写无断言测试。",
            "CI 里 coverage 报告帮助找未测分支；读报告看 missing lines。",
            "s15-l04-cov",
            "def sign(x):\n    return 0",
            "def sign(x):\n    return (x > 0) - (x < 0)",
            "assert sign(3) == 1 and sign(-1) == -1",
            ["覆盖错误路径", "测试应表达期望行为"],
            ["[pytest 文档](https://docs.pytest.org/en/stable/)"],
        ),
    ],
)

_stage(
    16,
    "16-工具链与项目结构",
    "工具链与项目结构",
    "L3",
    "ruff / mypy / pytest 在本仓库全绿",
    "examples/项目/16-项目模板/greeter/core.py",
    [
        _lesson(
            "01-src布局与pyproject",
            "src 布局与 pyproject",
            "5.2 包与项目结构",
            "[pyproject](https://packaging.python.org/en/latest/specifications/pyproject-toml/)",
            ["读懂 pyproject 的 project 与 dependency-groups", "知道 src 布局避免 import 污染"],
            """```python run
sample = '[project]\\nname = "demo"\\n'
print(sample.startswith("["))
```""",
            "-  editable 安装与 plain 脚本布局不同。\n- 锁文件 uv.lock 应与 pyproject 一致。",
            "本仓库 `uv run` 读取 pyproject；读依赖先看 `[project]` 与 `[dependency-groups]`。",
            "s16-l01-toml",
            "name = 'demo'",
            "name = 'demo'\nversion = '0.0.1'",
            "assert version == '0.0.1'",
            ["pyproject 是项目清单", "uv 管理锁与组"],
            [
                "[pyproject 规范](https://packaging.python.org/en/latest/specifications/pyproject-toml/)",
                "[uv 项目](https://docs.astral.sh/uv/guides/projects/)",
            ],
        ),
        _lesson(
            "02-ruff",
            "ruff 静态检查",
            "16.1 pyproject",
            "[Ruff](https://docs.astral.sh/ruff/)",
            ["会用 uv run ruff check", "区分格式与 lint 规则"],
            """```python run
# ruff 在 CI 中检查仓库 Python 代码；课内示例保持语法合法
x = 1 + 2
print(x)
```""",
            "- 自动 fix 可能改变语义，review diff。\n- 与 formatter 规则冲突时以团队配置为准。",
            "提交前跑 ruff；读 `[tool.ruff]` 了解忽略项。",
            "s16-l02-ruff",
            "def f():\n    return 0",
            "def f():\n    return 1",
            "assert f() == 1",
            ["ruff 速度快", "配置在 pyproject"],
            ["[Ruff linter](https://docs.astral.sh/ruff/linter/)"],
        ),
        _lesson(
            "03-mypy",
            "mypy 类型检查",
            "9. 类型注解",
            "[mypy](https://mypy.readthedocs.io/en/stable/)",
            ["运行 mypy 看静态类型错误", "理解 typing 与运行时无关"],
            """```python run
def greet(name: str) -> str:
    return f"hi, {name}"

print(greet("py"))
```""",
            "- Optional 与 `| None` 混用风格要统一。\n- 第三方缺 stubs 时用 `# type: ignore` 谨慎。",
            "SDK 带完整类型；本地模块 gradual typing 逐步加注解。",
            "s16-l03-mypy",
            "def add(a, b):\n    return str(a) + str(b)",
            "def add(a: int, b: int) -> int:\n    return a + b",
            "assert add(1, 2) == 3",
            ["mypy 静态分析", "注解不改变运行时"],
            ["[mypy 入门](https://mypy.readthedocs.io/en/stable/getting_started.html)"],
        ),
        _lesson(
            "04-logging配置与pdb",
            "logging 配置与 pdb",
            "8.6 logging",
            "[logging](https://docs.python.org/zh-cn/3/library/logging.html)",
            ["配置 basicConfig 或 dictConfig", "会用 pdb 断点调试"],
            """```python run
import logging
logging.basicConfig(level=logging.INFO)
logging.info("ready")
```""",
            "- root logger 多次 basicConfig 可能无效。\n- 生产环境用结构化日志而非 print。",
            "minimal_agent 可改为 logging；读配置看 level 与 handler。",
            "s16-l04-log",
            "def log_msg():\n    pass",
            "def log_msg():\n    return 'info'",
            "assert log_msg() == 'info'",
            ["logging 分级", "pdb 适合本地交互"],
            ["[logging HOWTO](https://docs.python.org/zh-cn/3/howto/logging.html)"],
        ),
    ],
)

_stage(
    17,
    "17-打包与发布",
    "打包与发布",
    "L3",
    "本地 uv build 产出 wheel 可安装",
    "examples/项目/17-CLI打包/logstats_pkg/cli.py",
    [
        _lesson(
            "01-wheel与构建后端",
            "wheel 与构建后端",
            "16.1 pyproject",
            "[打包教程](https://packaging.python.org/en/latest/tutorials/packaging-project/)",
            ["区分 wheel 与 sdist", "知道 build 后端在 pyproject 声明"],
            """```python run
# 构建在本地执行：uv build（课内仅示意命名）
name = "wheel"
print(name.endswith("heel"))
```""",
            "- 不要把 `.venv` 打进包。\n- 版本号遵循 semver 习惯。",
            "安装依赖时 pip/uv 优先 wheel；读 Packaging 用户指南。",
            "s17-l01-wheel",
            "pkg = 'sdist'",
            "pkg = 'wheel'",
            "assert pkg == 'wheel'",
            ["wheel 安装快", "sdist 需构建"],
            ["[packaging 教程](https://packaging.python.org/en/latest/tutorials/packaging-project/)"],
        ),
        _lesson(
            "02-版本与入口脚本",
            "版本与入口脚本",
            "5.2 包",
            "[entry points](https://packaging.python.org/en/latest/specifications/entry-points/)",
            ["在 pyproject 声明 console_scripts", "模块内写 main()"],
            """```python run
def main() -> int:
    print("cli")
    return 0

raise SystemExit(main())
```""",
            "- 入口函数应返回 int exit code。\n- 可编辑安装后命令在 .venv/bin。",
            "uv run 可直接跑模块；安装后 CLI 名由 entry point 决定。",
            "s17-l02-entry",
            "def main():\n    return 'x'",
            "def main():\n    return 0",
            "assert main() == 0",
            ["console_scripts 生成命令", "main 返回码"],
            ["[entry points](https://packaging.python.org/en/latest/specifications/entry-points/)"],
        ),
        _lesson(
            "03-发布流程",
            "发布流程（讲解）",
            "17.1 wheel",
            "[TestPyPI](https://packaging.python.org/en/latest/guides/using-testpypi/)",
            ["了解 twine/uv publish 流程", "本课程不在真 PyPI 发布"],
            """```python run
print("publish 仅文档演示，仓库不执行上传")
```""",
            "- 泄露 token 风险；用 CI secret。\n- 包名全局唯一。",
            "读 README 的发布章节即可；本 Goal 不要求真实 upload。",
            "s17-l03-pub",
            "step = 1",
            "step = 2",
            "assert step == 2",
            ["TestPyPI 演练", "真发布需审计"],
            ["[TestPyPI 指南](https://packaging.python.org/en/latest/guides/using-testpypi/)"],
        ),
    ],
)

_stage(
    18,
    "18-并发",
    "并发",
    "L4",
    "能按 I/O 或 CPU 密集选择 threading 或进程池",
    "examples/项目/18-并发下载模拟/downloader.py",
    [
        _lesson(
            "01-threading与GIL",
            "threading 与 GIL",
            "3. 控制流",
            "[threading](https://docs.python.org/zh-cn/3/library/threading.html)",
            ["知道 GIL 限制 CPU 并行", "I/O 阻塞时线程仍有用"],
            """```python run
# Pyodide 中不宜演示真实线程；本地完整示例见 examples/项目/18-并发下载模拟/
import threading
print("threading 模块可用", threading.__name__)
```""",
            "- 多线程改同一 int 可能丢更新（非原子）。\n- CPU 密集应用 multiprocessing 或 native 扩展。",
            "下载、等待 API 时常见线程/异步；读代码看阻塞点。",
            "s18-l01-thread",
            "import threading\n\nlock = threading.Lock()",
            "import threading\n\nlock = threading.Lock()\nacquired = lock.acquire(blocking=False)\nlock.release()",
            "assert acquired",
            ["GIL 与 CPU 并行", "I/O 等待可线程"],
            ["[threading](https://docs.python.org/zh-cn/3/library/threading.html)"],
        ),
        _lesson(
            "02-multiprocessing与futures",
            "multiprocessing 与 futures",
            "18.1 threading",
            "[concurrent.futures](https://docs.python.org/zh-cn/3/library/concurrent.futures.html)",
            ["用 ProcessPoolExecutor 并行 CPU 任务", "用 ThreadPoolExecutor 并行 I/O"],
            """```python run
from concurrent.futures import ThreadPoolExecutor
print("ThreadPoolExecutor", ThreadPoolExecutor)
```""",
            "- 子进程启动开销大。\n- 传递对象需可 pickle。",
            "批量请求 SDK 时可能用线程池；读 `max_workers` 与 map 语义。",
            "s18-l02-pool",
            "x = 1",
            "from concurrent.futures import ThreadPoolExecutor\n\npool = ThreadPoolExecutor",
            "assert pool.__name__ == 'ThreadPoolExecutor'",
            ["Executor 统一接口", "map 保序收集"],
            ["[concurrent.futures](https://docs.python.org/zh-cn/3/library/concurrent.futures.html)"],
        ),
        _lesson(
            "03-free-threaded现状",
            "free-threaded 现状",
            "18.1 threading",
            "[What's New 3.14](https://docs.python.org/zh-cn/3/whatsnew/3.14.html)",
            ["知道 3.14 起可选无 GIL 构建", "默认发行版仍多线程 + GIL"],
            """```python run
import sys
print(sys.version_info.major, sys.version_info.minor)
```""",
            "- free-threaded 与扩展 ABI 仍在演进。\n- 生产选型以官方支持声明为准（核对日期 2026-10-18）。",
            "读性能文章时注意 Python 版本与是否 nogil；3.10 已 EOL。",
            "s18-l03-ft",
            "py = (3, 9)",
            "py = (3, 12)",
            "assert py >= (3, 12)",
            ["3.14 起官方提供 free-threaded", "项目仍固定 3.12"],
            ["[What's New 3.14](https://docs.python.org/zh-cn/3/whatsnew/3.14.html)"],
        ),
    ],
)

_stage(
    19,
    "19-asyncio",
    "asyncio",
    "L4",
    "读懂 SDK 的 async 接口并能写简单协程",
    "examples/项目/19-异步minimal_agent/async_agent.py",
    [
        _lesson(
            "01-协程与事件循环",
            "协程与事件循环",
            "18. 并发",
            "[asyncio 入门](https://docs.python.org/zh-cn/3/library/asyncio.html)",
            ["定义 async def 与 await", "用 asyncio.run 驱动"],
            """```python run
import asyncio
import inspect

async def main():
    return 42

print(inspect.iscoroutinefunction(main))
```""",
            "- 在 async 函数里调用阻塞 IO 会卡住 loop。\n- 忘记 await 得到 coroutine 对象。",
            "新版 SDK 常提供 async client；搜 `async def create`。",
            "s19-l01-async",
            "import asyncio\n\nasync def f():\n    return 0",
            "import asyncio\n\nasync def f():\n    return 1\n\nf._lesson_tag = 1",
            "assert getattr(f, '_lesson_tag', None) == 1",
            ["async/await 语法", "asyncio.run 入口"],
            ["[asyncio](https://docs.python.org/zh-cn/3/library/asyncio.html)"],
        ),
        _lesson(
            "02-gather与TaskGroup",
            "gather 与 TaskGroup",
            "19.1 协程",
            "[TaskGroup](https://docs.python.org/zh-cn/3/library/asyncio-task.html#task-groups)（3.11 起）",
            ["并发多个 await", "TaskGroup 结构化并发"],
            """```python run
import asyncio
print(hasattr(asyncio, 'gather'))
```""",
            "- gather 默认 return_exceptions=False。\n- TaskGroup 任一失败会取消其余。",
            "并行 tool call 时可 asyncio.gather 多个请求（若 SDK 支持 async）。",
            "s19-l02-gather",
            "import asyncio\n\ngather = None",
            "import asyncio\n\ngather = asyncio.gather",
            "assert gather is asyncio.gather",
            ["gather 合并结果", "TaskGroup 3.11+"],
            ["[asyncio Task](https://docs.python.org/zh-cn/3/library/asyncio-task.html)"],
        ),
        _lesson(
            "03-异步HTTP概念",
            "异步 HTTP 概念",
            "19.2 gather",
            "[urllib](https://docs.python.org/zh-cn/3/library/urllib.request.html)",
            ["理解 async 客户端与连接池", "本课示例用标准库说明概念"],
            """```python run
# async HTTP 客户端在本地项目 examples/项目/22 中演示；课内用常量模拟状态码
status = 200
print(status)
```""",
            "- 在 async 函数里调用阻塞 socket 会卡住事件循环。\n- 生产用专用 async HTTP 客户端（见阶段 22）。",
            "读 SDK async 方法时看是否复用连接、是否需 `async with client`。",
            "s19-l03-http",
            "status = 404",
            "status = 200",
            "assert status == 200",
            ["I/O 用 async 避免阻塞 loop", "HTTP 层见 Web 阶段"],
            ["[urllib](https://docs.python.org/zh-cn/3/library/urllib.request.html)"],
        ),
    ],
)

# Fix lesson 19-02 gather exercise - the solution is wrong. Let me fix in place - asyncio.sleep doesn't take result=
# I'll fix the data file for s19-l02-gather

_stage(
    20,
    "20-性能",
    "性能",
    "L4",
    "能定位热点并做等价优化",
    "examples/项目/20-优化慢函数/slow_math.py",
    [
        _lesson(
            "01-timeit与cProfile",
            "timeit 与 cProfile",
            "18. 并发",
            "[timeit](https://docs.python.org/zh-cn/3/library/timeit.html)",
            ["用 timeit 比较小段代码", "知道 cProfile 看调用栈"],
            """```python run
import timeit
print(timeit.timeit("sum(range(100))", number=10000) < 1.0)
```""",
            "- 微基准易受噪声影响。\n- 先测再优化。",
            "怀疑慢函数时用 timeit/cProfile；不要凭感觉。",
            "s20-l01-time",
            "n = sum(range(9))",
            "n = sum(range(10))",
            "assert n == 45",
            ["测量先于优化", "timeit 重复多次"],
            ["[timeit](https://docs.python.org/zh-cn/3/library/timeit.html)"],
        ),
        _lesson(
            "02-复杂度与数据结构",
            "复杂度与数据结构",
            "4. 容器",
            "[时间复杂度](https://docs.python.org/zh-cn/3/tutorial/datastructures.html)",
            ["知道 list vs set 成员检测差异", "避免嵌套循环爆炸"],
            """```python run
items = list(range(1000))
target = 999
print(target in items)
```""",
            "- 频繁 `in list` 应改 set。\n- dict 按键 O(1) 平均。",
            "工具注册表用 dict 而非 list 扫描；读 TOOL_FUNCTIONS 即 dict。",
            "s20-l02-ds",
            "s = []\nassert 2 in s",
            "s = {1,2,3}\nassert 2 in s",
            "assert 2 in s",
            ["选对容器", "大 n 先看复杂度"],
            ["[数据结构](https://docs.python.org/zh-cn/3/tutorial/datastructures.html)"],
        ),
        _lesson(
            "03-常见优化",
            "常见优化",
            "20.1 timeit",
            "[性能提示](https://docs.python.org/zh-cn/3/faq/programming.html#what-is-the-most-efficient-way-to-concatenate-many-strings-in-python)",
            ["用 join 代替循环 += 拼字符串", "用局部变量减少属性查找"],
            """```python run
parts = ["a", "b", "c"]
print("".join(parts))
```""",
            "- 过早优化浪费。\n- 算法级优化优先于微优化。",
            "大量 JSON 拼接用 join 或 io.StringIO；读 hot path。",
            "s20-l03-opt",
            "s = ''\nfor p in ['a','b']:\n    s = s + p\ns = s + 'extra'",
            "s = ''.join(['a','b'])",
            "assert s == 'ab'",
            ["join 拼字符串", "先 profile"],
            ["[FAQ 性能](https://docs.python.org/zh-cn/3/faq/programming.html)"],
        ),
    ],
)

_stage(
    21,
    "21-数据",
    "数据",
    "L5",
    "完成小 CSV 分析",
    "examples/项目/21-CSV分析报告/analyze.py",
    [
        _lesson(
            "01-NumPy入门",
            "NumPy 入门",
            "2.2 数字",
            "[NumPy 用户指南](https://numpy.org/doc/stable/user/index.html)",
            ["知道 ndarray 与向量化", "示例在本地项目运行"],
            """```python run
# 课内 Pyodide 无 NumPy；用纯 Python 模拟向量加法
a = [1, 2, 3]
b = [4, 5, 6]
print([x + y for x, y in zip(a, b)])
```""",
            "- NumPy 数组与 list 不同。\n- 广播规则易错，需查文档。",
            "数据分析栈底层 NumPy；pandas Series 基于 ndarray。",
            "s21-l01-np",
            "a = [1]\nb = [2]\nvec = [0]",
            "a = [1]\nb = [2]\nvec = [x+y for x,y in zip(a,b)]",
            "assert vec == [3]",
            ["向量化避免 Python 循环", "本地 uv sync --group data"],
            ["[NumPy 文档](https://numpy.org/doc/stable/)"],
        ),
        _lesson(
            "02-pandas入门",
            "pandas 入门",
            "21.1 NumPy",
            "[pandas 入门](https://pandas.pydata.org/docs/getting_started/index.html)",
            ["会用 DataFrame 读 CSV", "会做 groupby 聚合"],
            """```python run
import csv
from io import StringIO
from collections import defaultdict
text = "city,temp\\n上海,22\\n北京,18\\n"
rows = list(csv.DictReader(StringIO(text)))
by = defaultdict(list)
for r in rows:
    by[r['city']].append(float(r['temp']))
print({k: sum(v)/len(v) for k,v in by.items()})
```""",
            "- SettingWithCopy 警告。\n- 大表注意 dtype 与内存。",
            "报告型任务 pandas 一行 read_csv；读代码先看 columns 与 index。",
            "s21-l02-pd",
            "rows = [{'a': 1}]\nval = rows[0].get('b')",
            "rows = [{'a': 1}]\nval = rows[0]['a']",
            "assert val == 1",
            ["DataFrame 像带标签表", "groupby 聚合"],
            ["[pandas 文档](https://pandas.pydata.org/docs/)"],
        ),
        _lesson(
            "03-Jupyter",
            "Jupyter 工作流",
            "21.2 pandas",
            "[JupyterLab](https://jupyter.org/documentation)",
            ["知道 notebook 适合探索", "最终逻辑仍应回到 .py 与测试"],
            """```python run
print("notebook 在浏览器编辑；本仓库用 Markdown + Pyodide 课")
```""",
            "- notebook 难 code review。\n- 输出顺序可能乱。",
            "探索数据用 Jupyter；交付用脚本与 pytest。",
            "s21-l03-jup",
            "mode = 'explore'",
            "mode = 'script'",
            "assert mode == 'script'",
            ["Jupyter 交互探索", "生产用模块+测试"],
            ["[Jupyter 文档](https://jupyter.org/documentation)"],
        ),
    ],
)

_stage(
    22,
    "22-Web与API",
    "Web 与 API",
    "L5",
    "写出带测试的 FastAPI",
    "examples/项目/22-天气工具API/app.py",
    [
        _lesson(
            "01-HTTP与ASGI",
            "HTTP 与 ASGI",
            "19.3 异步 HTTP",
            "[HTTP 概述](https://docs.python.org/zh-cn/3/library/http.html)",
            ["理解请求/响应/status", "ASGI 是 async 应用协议"],
            """```python run
from http import HTTPStatus
print(HTTPStatus.OK.value, HTTPStatus.NOT_FOUND.value)
```""",
            "- GET 不应有副作用。\n- 5xx 与 4xx 责任不同。",
            "SDK REST 调用对应 HTTP；读 status_code 与 json()。",
            "s22-l01-http",
            "code = 404",
            "code = 200",
            "assert code == 200",
            ["HTTP 语义", "ASGI 连接 async 框架"],
            ["[http 模块](https://docs.python.org/zh-cn/3/library/http.html)"],
        ),
        _lesson(
            "02-FastAPI与Pydantic",
            "FastAPI 与 Pydantic",
            "9. 类型注解",
            "[FastAPI 教程](https://fastapi.tiangolo.com/tutorial/)",
            ["路由函数返回模型", "Pydantic 校验请求/响应"],
            """```python run
# FastAPI 在本地 examples/项目/22；课内用 dataclass 模拟模型
from dataclasses import dataclass

@dataclass
class WeatherOut:
    city: str
    summary: str

print(WeatherOut("上海", "晴"))
```""",
            "- 依赖注入在 FastAPI 很常见。\n- 自动 OpenAPI 文档。",
            "写 API 与读 SDK 相反：你定义 schema；仍用类型注解。",
            "s22-l02-fa",
            "class M:\n    pass",
            "class M:\n    def __init__(self, x):\n        self.x = x",
            "assert M(1).x == 1",
            ["FastAPI 基于类型提示", "Pydantic v2 校验"],
            [
                "[FastAPI](https://fastapi.tiangolo.com/tutorial/)",
                "[Pydantic](https://docs.pydantic.dev/latest/)",
            ],
        ),
        _lesson(
            "03-测试API",
            "测试 API",
            "15. pytest",
            "[TestClient](https://fastapi.tiangolo.com/tutorial/testing/)",
            ["用 TestClient 不发真实网络", "断言 status 与 JSON"],
            """```python run
# 逻辑测试：模拟响应 dict
resp = {"city": "上海", "summary": "晴"}
assert resp["city"] == "上海"
```""",
            "- 测试应隔离数据库。\n- 覆盖 404/422。",
            "与测 CLI 类似：调用函数/客户端，断言结构化输出。",
            "s22-l03-api",
            "resp = {}",
            "resp = {'ok': True}",
            "assert resp['ok']",
            ["TestClient 同步测 async app", "断言 schema"],
            ["[FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)"],
        ),
    ],
)

_stage(
    23,
    "23-Agent实战",
    "Agent 实战",
    "L5",
    "把 minimal_agent 思路改成可测小模块",
    "examples/项目/23-mini-agent包/mini_agent/runner.py",
    [
        _lesson(
            "01-工具调用协议",
            "工具调用协议",
            "11. minimal_agent",
            "[Anthropic 消息 API](https://docs.python.org/zh-cn/3/tutorial/index.html)",
            ["理解 tools 列表与 tool_use 块", "TOOL_FUNCTIONS 映射 name→callable"],
            """```python run
TOOLS = {"get_weather": lambda city: f"{city}:晴"}
name = "get_weather"
print(TOOLS[name]("上海"))
```""",
            "- 工具 schema 要与函数参数一致。\n- 未注册 name 会 KeyError。",
            "minimal_agent 中 TOOL_FUNCTIONS 即注册表；读 tools JSON schema。",
            "s23-l01-tool",
            "REG = {}",
            "REG = {'echo': lambda x: x}",
            "assert REG['echo']('a') == 'a'",
            ["schema 描述参数", "运行时查 REGISTRY"],
            ["[Python 教程](https://docs.python.org/zh-cn/3/tutorial/index.html)"],
        ),
        _lesson(
            "02-多工具与错误处理",
            "多工具与错误处理",
            "23.1 工具协议",
            "[异常](https://docs.python.org/zh-cn/3/tutorial/errors.html)",
            ["工具执行 try/except 回传错误", "并行 tool call 需合并结果"],
            """```python run
def run_tool(name, **kw):
    if name == "fail":
        raise ValueError("bad")
    return name

try:
    run_tool("fail")
except ValueError as e:
    print(str(e))
```""",
            "- 把异常直接抛给用户不友好。\n- 记录日志便于排查。",
            "Agent 循环里应对 SDK/工具异常做分支，避免整轮崩溃。",
            "s23-l02-err",
            "def safe(x):\n    return x",
            "def safe(x):\n    try:\n        return 1/x\n    except ZeroDivisionError:\n        return None",
            "assert safe(0) is None",
            ["错误应变成模型可读消息", "不要裸 raise 到顶层"],
            ["[错误和异常](https://docs.python.org/zh-cn/3/tutorial/errors.html)"],
        ),
        _lesson(
            "03-流式输出",
            "流式输出",
            "10.1 生成器",
            "[迭代器](https://docs.python.org/zh-cn/3/tutorial/classes.html#iterators)",
            ["理解 stream 迭代 partial 响应", "终端打印与累积完整消息"],
            """```python run
def stream():
    for chunk in ("你", "好"):
        yield chunk

print("".join(stream()))
```""",
            "- 流式下 tool call 可能分片到达。\n- 需要缓冲拼完整 JSON。",
            "SDK `stream=True` 时读事件迭代；读代码找 for event in ...。",
            "s23-l03-stream",
            "def stream():\n    return iter([])",
            "def stream():\n    yield 'a'",
            "assert list(stream()) == ['a']",
            ["生成器表达流", "Agent UX 常用流式"],
            ["[迭代器](https://docs.python.org/zh-cn/3/tutorial/classes.html#iterators)"],
        ),
    ],
)

_stage(
    24,
    "24-Python内部",
    "Python 内部",
    "L6",
    "能解释常见怪现象",
    "",
    [
        _lesson(
            "01-名字绑定与对象模型",
            "名字绑定与对象模型",
            "2.1 语法骨架",
            "[命名与绑定](https://docs.python.org/zh-cn/3/reference/executionmodel.html#naming-and-binding)",
            ["名字是标签，对象是独立实体", "赋值不复制对象，只绑定名字"],
            """```python run
a = [1, 2]
b = a
b.append(3)
print(a, b is a)
```""",
            "- 默认参数可变对象陷阱。\n- `is` 与 `==` 不同。",
            "messages 列表在多轮中原地修改；多个名字可指向同一 list。",
            "s24-l01-bind",
            "x = [1]\ny = x",
            "x = [1]\ny = x\nx.append(2)",
            "assert y == [1, 2]",
            ["赋值绑定名字", "可变对象共享"],
            ["[执行模型](https://docs.python.org/zh-cn/3/reference/executionmodel.html)"],
        ),
        _lesson(
            "02-字节码dis",
            "字节码 dis",
            "3.2 函数",
            "[dis 模块](https://docs.python.org/zh-cn/3/library/dis.html)",
            ["会用 dis.dis 看 opcode", "理解 LOAD/STORE/CALL"],
            """```python run
import dis

def add(a, b):
    return a + b

dis.dis(add)
print("shown")
```""",
            "- 字节码因版本而异。\n- 仅调试/原理用，日常不必背 opcode。",
            "性能极热点才看字节码；读怪行为先查数据模型。",
            "s24-l02-dis",
            "def f():\n    return 0",
            "def f():\n    return 1",
            "assert f() == 1",
            ["dis 展示栈机指令", "CPython 实现细节"],
            ["[dis](https://docs.python.org/zh-cn/3/library/dis.html)"],
        ),
        _lesson(
            "03-内存与GC",
            "内存与 GC",
            "24.1 名字绑定",
            "[gc 模块](https://docs.python.org/zh-cn/3/library/gc.html)",
            ["引用计数为主，循环引用靠 gc", "弱引用了解即可"],
            """```python run
import sys
a = []
print(sys.getrefcount(a) >= 1)
```""",
            "- 循环引用需要 gc 收集。\n- 大对象注意 __slots__（进阶）。",
            "长生命周期 Agent 会话注意 messages 列表增长。",
            "s24-l03-gc",
            "a = object()",
            "a = object()\nb = a",
            "assert b is a",
            ["引用计数即时回收", "循环引用 gc 周期"],
            ["[gc](https://docs.python.org/zh-cn/3/library/gc.html)"],
        ),
        _lesson(
            "04-导入系统",
            "导入系统",
            "5.1 模块与 import",
            "[importlib](https://docs.python.org/zh-cn/3/library/importlib.html)",
            ["理解 sys.modules 缓存", "包相对导入与 __package__"],
            """```python run
import sys
print("sys" in sys.modules)
```""",
            "- 循环 import 导致部分初始化。\n- 动态 import 难静态分析。",
            "读项目先看 import 块；第三方包在 site-packages。",
            "s24-l04-imp",
            "name = 'sys'",
            "import json\nname = json.__name__",
            "assert name == 'json'",
            ["首次 import 执行模块顶层", "sys.modules 缓存"],
            ["[导入系统](https://docs.python.org/zh-cn/3/reference/import.html)"],
        ),
    ],
)
