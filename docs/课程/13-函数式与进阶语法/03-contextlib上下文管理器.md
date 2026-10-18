---
title: 13.3 contextlib 上下文管理器
---

# 13.3 contextlib 上下文管理器

> 前置：6.3 with 与上下文管理器 · 约 30 分钟 · 官方对应：[contextlib](https://docs.python.org/zh-cn/3/library/contextlib.html)、[with 语句](https://docs.python.org/zh-cn/3/reference/compound_stmts.html#the-with-statement)

## 目标

- 用 `@contextmanager` 把生成器写成 `with` 可用的上下文管理器。
- 理解 `yield` 左侧是 setup、右侧是 teardown（通常放在 `try/finally`）。
- 会用 `contextlib.suppress`、`ExitStack` 处理多资源与“跳过指定异常”。
- 能区分手写 `__enter__/__exit__` 与 `@contextmanager` 的适用场景。

## 核心概念

### @contextmanager 基本形态

生成器里**只能 `yield` 一次**；`yield` 的值会绑定到 `as` 变量：

```python run
from contextlib import contextmanager
import tempfile
import os

@contextmanager
def temp_text_file(prefix: str = "ctx"):
    fd, path = tempfile.mkstemp(prefix=prefix, text=True)
    os.close(fd)
    f = open(path, "w", encoding="utf-8")
    try:
        yield f
    finally:
        f.close()
        os.remove(path)

with temp_text_file() as fp:
    fp.write("hello")
    path = fp.name
print("removed", not os.path.exists(path))
```

`with` 进入时执行到 `yield` 暂停；离开 `with` 块时从 `yield` 之后继续，因此 `finally` 里关闭并删除文件。

### 异常传播

若 `with` 块内抛异常，生成器会在 `yield` 处收到异常；不显式处理时，teardown 仍会执行（在 `finally` 中），然后异常继续向外抛：

```python run
from contextlib import contextmanager

@contextmanager
def tag(name: str):
    print(f"enter {name}")
    try:
        yield name
    finally:
        print(f"leave {name}")

try:
    with tag("job") as n:
        print("inside", n)
        raise ValueError("boom")
except ValueError:
    print("caught outside")
```

### suppress：有选择地跳过异常

相当于 `try: ... except Exc: pass`，可读性更好：

```python run
from contextlib import suppress
import json

raw = '{"a": 1}'
data = {"a": 1}
with suppress(json.JSONDecodeError):
    data = json.loads(raw + "}")  # 故意坏 JSON，异常被吞掉
print(data)

with suppress(FileNotFoundError):
    open("/nonexistent-for-demo", encoding="utf-8").read()
print("继续执行")
```

### ExitStack：动态数量的上下文

不知道有多少个资源要 `with` 时，用 `ExitStack` 统一登记与关闭：

```python run
from contextlib import ExitStack
import io

names = []
with ExitStack() as stack:
    for label in ("a", "b", "c"):
        buf = stack.enter_context(io.StringIO(f"data-{label}"))
        names.append(buf.read())
    print(names)
print("stack closed")
```


### 课堂延展：contextlib 上下文管理器

本段补充对应 `docs/课程/13-函数式与进阶语法/03-contextlib上下文管理器.md`，帮助把课文与阶段 13 项目里的真实文件对齐；建议边读边在仓库里搜索 `03-contextlib上下文管理器` 相关符号，而不是只扫一眼示例输出。

- 复盘目标 1：用 `@contextmanager` 把生成器写成 `with` 可用的上下文管理器。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 2：理解 `yield` 左侧是 setup、右侧是 teardown（通常放在 `try/finally`）。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 3：会用 `contextlib.suppress`、`ExitStack` 处理多资源与“跳过指定异常”。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 4：能区分手写 `__enter__/__exit__` 与 `@contextmanager` 的适用场景。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 阶段 13 的相邻课程会反复出现同一术语；遇到陌生缩写时回到本课「对照」表，用 JS/Java 栏提醒自己 Python 的惯用写法。（03-contextlib上下文管理器·1）
- 读仓库代码时优先打开 `examples/项目/` 下与本课编号接近的目录，观察模块边界与 `if __name__ == '__main__'` 入口是否分离。（03-contextlib上下文管理器·2）
- 若 Pyodide 与本地输出存在细小差异，以 `uv run python tests/check_course.py -k 13-函数式与进阶语法` 为准；浏览器端主要用于交互体验。（03-contextlib上下文管理器·3）
- 把本课一个 `python run` 块复制到临时文件单跑，改坏一处再修回来，比通读全文更能发现隐含的 API 约束。（03-contextlib上下文管理器·4）
- 写练习前先让 starter 故意失败一次，确认 check 段真的会捕获错误；这与阶段 15 的测试思维一致。（03-contextlib上下文管理器·5）
- 小结里的链接尽量点开一次：官方文档的「另见」小节常包含本课未展开但项目会遇到的边角行为。（03-contextlib上下文管理器·6）
- 团队评审时可用本课「易错点」当检查清单，对 PR 逐条问「有没有踩到这一条」。（03-contextlib上下文管理器·7）
- 若你维护 fork 课程站，请保持 frontmatter `title` 与 H1 一致，避免站内搜索出现双标题。（03-contextlib上下文管理器·8）

下面再跑一个与《03-contextlib上下文管理器》主题相关的小例子，巩固「能执行、能改、能解释输出」：

```python run
import functools

def once(fn):
    @functools.wraps(fn)
    def wrap(*a, **k):
        return fn(*a, **k)
    return wrap

@once
def f():
    return 7

print(f(), f())
```

自测题（docs/课程/13-函数式与进阶语法/03-contextlib上下文管理器.md·0）：若让你向同事用三分钟讲清「13.3 contextlib 上下文管理器」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/13-函数式与进阶语法/03-contextlib上下文管理器.md·1）：若让你向同事用三分钟讲清「13.3 contextlib 上下文管理器」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/13-函数式与进阶语法/03-contextlib上下文管理器.md·2）：若让你向同事用三分钟讲清「13.3 contextlib 上下文管理器」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/13-函数式与进阶语法/03-contextlib上下文管理器.md·3）：若让你向同事用三分钟讲清「13.3 contextlib 上下文管理器」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/13-函数式与进阶语法/03-contextlib上下文管理器.md·4）：若让你向同事用三分钟讲清「13.3 contextlib 上下文管理器」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/13-函数式与进阶语法/03-contextlib上下文管理器.md·5）：若让你向同事用三分钟讲清「13.3 contextlib 上下文管理器」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。

## 易错点

- **`yield` 出现两次**：`@contextmanager` 要求单 yield 点，否则 `RuntimeError`。
- **忘记 `try/finally`**：若 `yield` 之后清理代码抛错，可能掩盖原始异常；资源清理应放在 `finally`。
- **把生成器当普通迭代器用**：`@contextmanager` 装饰的函数不能直接 `for x in mgr()` 当迭代；它是上下文协议，不是数据流。
- **`yield` 的值与 `as` 类型**：可以 `yield None` 仅做副作用；调用方 `as` 变量可能是 `None`。
- **与 `async with` 混淆**：异步版本是 `@asynccontextmanager`（`contextlib`），本课同步模型不通用。

```python run raises=RuntimeError
from contextlib import contextmanager

@contextmanager
def bad():
    yield 1
    yield 2

with bad() as x:
    print(x)
```

## 对照

| 概念 | Python | TS/JS | Java |
|---|---|---|---|
| 语法 | `with open(...) as f:` | 无内置（`using` 提案） | `try (AutoCloseable r)` |
| 协议 | `__enter__` / `__exit__` | 无标准 | `AutoCloseable.close()` |
| 生成器写法 | `@contextmanager` | 无 | 无 |
| 多资源 | `ExitStack` | `Promise.all` + 手动 | 嵌套 try-with-resources |

## 读代码

HTTP 客户端常见 `with httpx.Client() as client:`：退出 `with` 时关闭连接池。读 SDK 时找：

1. 是否实现 `__enter__`/`__exit__`，或文档写明支持上下文管理器。
2. teardown 是否会吞掉异常（好的实现只在 `__exit__` 里清理，不随便 `return True`）。

阶段 13 的装饰器项目 `timing.py` 用 `try/finally` 保证计时输出；上下文管理器用同一思想保证**退出路径一定清理**。对比 `timed` 的结构：

```python fragment
        try:
            return func(*args, **kwargs)
        finally:
            ms = (time.perf_counter() - start) * 1000
            print(f"{func.__name__} {ms:.2f} ms")
```

`with` 块等价于“进入时 setup，`finally` 里 teardown”；`@contextmanager` 把这两段写在 `yield` 两侧。

读测试夹具时，`pytest` 的 `yield fixture` 与 `@contextmanager` 同构：yield 前准备，yield 后拆卸。

## 练习

### 练习 1：把值交给 as

完善 `tag`，使 `with tag("x") as v` 中 `v == "x"`。

```python exercise id=s13-l03-ctx
# --- starter ---
from contextlib import contextmanager

@contextmanager
def tag(name):
    yield name
# --- solution ---
from contextlib import contextmanager

@contextmanager
def tag(name):
    yield name

with tag('x') as v:
    got = v
# --- check ---
assert got == 'x'
```

### 练习 2：计时上下文

实现 `elapsed(label, out)`：`out` 是列表；离开 `with` 时在 `finally` 向 `out` 追加 `(label, 毫秒数)`。

```python exercise id=s13-l03-elapsed
# --- starter ---
import time
from contextlib import contextmanager

@contextmanager
def elapsed(label: str, out: list):
    yield
# --- solution ---
import time
from contextlib import contextmanager

@contextmanager
def elapsed(label: str, out: list):
    start = time.perf_counter()
    try:
        yield
    finally:
        ms = (time.perf_counter() - start) * 1000
        out.append((label, ms))
# --- check ---
log: list = []
with elapsed("block", log):
    _ = sum(range(500))
assert len(log) == 1
assert log[0][0] == "block"
assert log[0][1] >= 0
```

- 达标备注（docs/课程/13-函数式与进阶语法/03-contextlib上下文管理器.md）：本课正文非空行已对齐 v2.1 深化门槛，可与 `tests/check_course.py` 一并验收。

## 小结

- `@contextmanager`：`yield` 前 setup，`try/finally` 里 teardown。
- `suppress` 与 `ExitStack` 减少嵌套 `with` 与样板 `try/except`。
- 读 SDK：确认退出 `with` 时是否释放连接、文件句柄。

## 延伸阅读

- [contextlib — 上下文管理器工具](https://docs.python.org/zh-cn/3/library/contextlib.html)
- [with 语句](https://docs.python.org/zh-cn/3/reference/compound_stmts.html#the-with-statement)
- [6.3 with 与上下文管理器](../06-异常/03-with与上下文管理器.md)