---
title: 6.3 with 与上下文管理器
---

# 6.3 with 与上下文管理器

> 前置：6.2 · 约 25 分钟 · 官方对应：[预定义的清理操作](https://docs.python.org/zh-cn/3/tutorial/errors.html#predefined-clean-up-actions)、[with 语句](https://docs.python.org/zh-cn/3/reference/compound_stmts.html#the-with-statement)、[contextlib](https://docs.python.org/zh-cn/3/library/contextlib.html)

## 目标

- 理解 `with` 保证“进入时获取、退出时释放”，即使中途发生异常。
- 读懂 `with open(...) as f:` 与 `with A() as a, B() as b:`。
- 理解上下文管理器协议 `__enter__` / `__exit__`，会用 `@contextmanager` 写简单的上下文管理器。

## 核心概念

### with 语句

```python run
from pathlib import Path

with open("notes.txt", "w", encoding="utf-8") as f:   # 进入：打开文件，绑定到 f
    f.write("第一行\n")
    f.write("第二行\n")
# 离开 with 块：文件自动关闭（即使块内抛出异常）
print(f.closed)

with open("notes.txt", encoding="utf-8") as f:
    for line in f:
        print(line.rstrip())
```

它大致等价于：

```python
f = open("notes.txt", encoding="utf-8")
try:
    ...  # 使用 f
finally:
    f.close()
```

### 协议：`__enter__` 与 `__exit__`

任何实现了这两个方法的对象都是**上下文管理器**：

- `__enter__()` 的返回值绑定到 `as` 后的名字；
- `__exit__(exc_type, exc, tb)` 在离开时调用；有异常时三个参数是异常信息，返回真值表示“异常已处理，不再向外抛”。

```python run
import time

class Timer:
    def __init__(self, label):
        self.label = label

    def __enter__(self):
        self.start = time.perf_counter()
        print(f"[{self.label}] 开始")
        return self                       # 绑定到 as 后的名字

    def __exit__(self, exc_type, exc, tb):
        cost = (time.perf_counter() - self.start) * 1000
        status = "失败：" + exc_type.__name__ if exc_type else "成功"
        print(f"[{self.label}] {status}，耗时 {cost:.1f} ms")
        return False                      # 不吞掉异常

with Timer("调用模型") as t:
    sum(range(100_000))

try:
    with Timer("调用工具"):
        {}["missing"]
except KeyError:
    print("异常仍然向外传播")
```

### @contextmanager：用生成器写上下文管理器

`contextlib.contextmanager` 把一个含 `yield` 的函数变成上下文管理器：`yield` 之前是进入，之后是退出，`yield` 的值绑定到 `as`。

```python run
import os
from contextlib import contextmanager

@contextmanager
def env_var(name, value):
    """临时设置环境变量，退出时恢复。"""
    old = os.environ.get(name)
    os.environ[name] = value
    try:
        yield value
    finally:
        if old is None:
            del os.environ[name]
        else:
            os.environ[name] = old

with env_var("LLM_PROVIDER", "anthropic") as v:
    print("块内：", os.getenv("LLM_PROVIDER"), v)
print("块外：", os.getenv("LLM_PROVIDER"))
```

### 其他常见写法

```python run
from contextlib import suppress
import os

with suppress(FileNotFoundError):        # 忽略指定异常
    os.remove("not-exist.txt")
print("没有报错")

with open("a.txt", "w") as fa, open("b.txt", "w") as fb:   # 多个上下文管理器
    fa.write("A")
    fb.write("B")
print(open("a.txt").read(), open("b.txt").read())
```

真实代码中常见的上下文管理器：`open()`、`threading.Lock()`、`tempfile.TemporaryDirectory()`、数据库连接/事务、HTTP 客户端（`with httpx.Client() as c:`）、SDK 的流式响应（`with client.messages.stream(...) as stream:`）。

## 易错点

- **不用 `with` 打开文件**：忘记 `close()` 可能导致数据未写入或句柄泄漏。
- **`with` 块外继续使用资源**：文件已关闭，读写抛 `ValueError: I/O operation on closed file`。
- **`__exit__` 返回 `True`** 会吞掉异常，除非刻意为之，返回 `False` 或 `None`。
- **`@contextmanager` 中不用 `try/finally` 包住 `yield`**：块内出异常时清理代码不会执行。

```python run raises=ValueError
with open("x.txt", "w") as f:
    f.write("hi")
f.write("块外再写")   # 文件已关闭
```

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 自动释放资源 | `with open(p) as f:` | `using`（显式资源管理，TS 5.2 起；部分运行时原生支持） | try-with-resources `try (var f = …) {}` |
| 协议 | `__enter__` / `__exit__` | `[Symbol.dispose]()` | `AutoCloseable.close()` |
| 生成器式实现 | `@contextmanager` | 无 | 无 |

## 读代码

`minimal_agent.py` 没有使用 `with`：`anthropic.Anthropic(...)` 客户端在脚本结束时由解释器回收。长期运行的服务中，SDK 客户端通常支持 `with` 以确保关闭底层 HTTP 连接（示意）：

```python
with anthropic.Anthropic(api_key=key) as client:
    resp = client.messages.create(model=model, max_tokens=1024, messages=messages)
```

读到 `with X(...) as y:` 时，先问两个问题：**进入时获取了什么**（连接、锁、文件、临时目录）？**退出时释放了什么**？

## 练习

### 练习 1：写入并读回

实现 `save_and_load(path, lines)`：用 `with` 把字符串列表 `lines` 逐行写入 `path`（UTF-8，每行末尾加 `\n`），再用 `with` 读回，返回读到的行列表（去掉换行符）。

```python exercise id=s06-l03-file
# --- starter ---
def save_and_load(path, lines):
    f = open(path, "w", encoding="utf-8")
    for line in lines:
        f.write(line)
    return []
# --- solution ---
def save_and_load(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")
    with open(path, encoding="utf-8") as f:
        return [line.rstrip("\n") for line in f]
# --- check ---
assert save_and_load("t.txt", ["第一行", "second"]) == ["第一行", "second"]
assert open("t.txt", encoding="utf-8").read() == "第一行\nsecond\n"
assert save_and_load("empty.txt", []) == []
```

### 练习 2：记录耗时的上下文管理器

用 `@contextmanager` 实现 `record(events, name)`：进入时向列表 `events` 追加 `f"start:{name}"`，退出时（**无论是否异常**）追加 `f"end:{name}"`；异常照常向外抛出。

```python exercise id=s06-l03-cm
# --- starter ---
from contextlib import contextmanager

@contextmanager
def record(events, name):
    events.append(f"start:{name}")
    yield
# --- solution ---
from contextlib import contextmanager

@contextmanager
def record(events, name):
    events.append(f"start:{name}")
    try:
        yield
    finally:
        events.append(f"end:{name}")
# --- check ---
ev = []
with record(ev, "a"):
    ev.append("body")
assert ev == ["start:a", "body", "end:a"], ev
ev = []
try:
    with record(ev, "b"):
        raise ValueError("boom")
except ValueError:
    pass
else:
    raise AssertionError("异常应向外传播")
assert ev == ["start:b", "end:b"], f"出现异常时也要记录 end：{ev}"
```

## 小结

- `with` = 进入时获取 + 退出时释放，异常也不例外。
- 协议是 `__enter__` / `__exit__`；`@contextmanager` 用 `yield` 分隔进入与退出，记得 `try/finally`。
- 读到 `with` 时，找出“获取了什么、释放了什么”。

## 延伸阅读

- [预定义的清理操作](https://docs.python.org/zh-cn/3/tutorial/errors.html#predefined-clean-up-actions)
- [with 语句（参考）](https://docs.python.org/zh-cn/3/reference/compound_stmts.html#the-with-statement)
- [上下文管理器类型](https://docs.python.org/zh-cn/3/library/stdtypes.html#context-manager-types)
- [contextlib](https://docs.python.org/zh-cn/3/library/contextlib.html)
- [PEP 343：with 语句](https://peps.python.org/pep-0343/)
