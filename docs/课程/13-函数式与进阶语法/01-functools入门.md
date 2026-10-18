---
title: 13.1 functools 入门
---

# 13.1 functools 入门

> 前置：10.2 装饰器 · 约 30 分钟 · 官方对应：[functools](https://docs.python.org/zh-cn/3/library/functools.html) · 核对日期 2026-10-18（正文对 Python 3.12–3.15 成立）

## 目标

- 用 `functools.partial` 预先绑定参数，得到“少几个形参”的可调用对象。
- 用 `functools.lru_cache` / `cache` 为**纯函数**做结果记忆化，并读懂 `cache_info()`。
- 用 `functools.wraps` 保留被装饰函数的 `__name__`、`__doc__` 等元信息。
- 知道 `cached_property` 与 `lru_cache` 的适用场景差异（对象属性 vs 函数调用）。

## 核心概念

### partial：固定部分参数

`partial(func, *args, **kwargs)` 返回一个新可调用对象，调用时再补上剩余参数：

```python run
import functools

def power(base: int, exp: int) -> int:
    return base ** exp

square = functools.partial(power, exp=2)
cube = functools.partial(power, exp=3)

print(square(5), cube(2))
print(power(2, 10), square.args, square.keywords)
```

常见用途：把 `print` 绑定 `flush=True`，或把回调的第一个参数固定为 `self`。

### lru_cache 与 cache

`lru_cache(maxsize=128)` 用 LRU 策略缓存**可哈希参数**下的返回值；`maxsize=None` 表示不设上限。Python 3.9 起可用 `@functools.cache`（等价于 `lru_cache(maxsize=None)`）：

```python run
import functools

@functools.lru_cache(maxsize=32)
def fib(n: int) -> int:
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

print(fib(20))
info = fib.cache_info()
print(info.hits, info.misses, info.currsize)

@functools.cache
def slug(text: str) -> str:
    return text.strip().lower().replace(" ", "-")

print(slug("Hello World"), slug.cache_info())
```

斐波那契从指数级递归调用降为线性次实际计算，靠的是**相同 `n` 只算一次**。

### wraps：装饰器必备

阶段项目 `timing.py` 里的 `timed` 与 10.2 模板一样，核心就是 `@functools.wraps(func)`：

```python run
import functools
import time

def timed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            ms = (time.perf_counter() - start) * 1000
            print(f"{func.__name__} {ms:.2f} ms")
    return wrapper

@timed
def work(n: int) -> int:
    """累加 0..n-1。"""
    return sum(range(n))

print(work(100_000), work.__name__, work.__doc__)
```

没有 `wraps` 时，`work.__name__` 会变成 `wrapper`，测试与文档工具都会误导。

### reduce 与 cmp_to_key（了解）

`functools.reduce` 把二元函数从左到右折叠序列；`cmp_to_key` 把旧式比较函数转成 `sorted` 的 `key`（现代代码更常用 `key=lambda`）：

```python run
import functools
import operator

print(functools.reduce(operator.add, [1, 2, 3, 4], 0))
pairs = [(3, "c"), (1, "a"), (2, "b")]
print(sorted(pairs, key=operator.itemgetter(0)))
```

| API | 作用 | 注意 |
|---|---|---|
| `partial` | 绑定部分参数 | 新对象有 `.func`、`.args`、`.keywords` |
| `lru_cache` | 有界 LRU 缓存 | 参数须可哈希；可变默认参数要小心 |
| `cache` | 无界缓存（3.9+） | 只适合参数空间小的纯函数 |
| `wraps` | 复制元信息到 wrapper | 装饰器几乎总是需要 |
| `cached_property` | 实例上算一次 | 见 10.4 / 12.3 |


## 易错点

- **`lru_cache` 的参数必须可哈希**：传入 `list` 或自定义未实现 `__hash__` 的对象会 `TypeError`。
- **缓存了可变对象**：若函数返回同一可变列表，调用方修改会影响“缓存里的值”；纯函数应返回新对象或不可变类型。
- **把有副作用的函数放进 cache**：日志、写文件、随机数都会被跳过第二次调用，行为错误。
- **忘记 `@wraps`**：`help(fn)`、`pytest` 节点名、`functools` 链式装饰都会显示 `wrapper`。
- **`partial` 与 `*args` 顺序**：先绑定的位置参数占坑，剩余参数按原函数签名补齐，读 `partial.__repr__` 可核对。

```python run raises=TypeError
import functools

@functools.lru_cache
def bad(items: list) -> int:
    return len(items)

bad([1, 2])
```

## 对照

| 概念 | Python | TS/JS | Java |
|---|---|---|---|
| 偏函数 | `functools.partial` | 手动闭包或 lodash `partial` | 无标准库，常手写 |
| 记忆化 | `lru_cache` / `cache` | 手写 `Map` 或 memo 库 | `LoadingCache`（Guava）等 |
| 装饰器元信息 | `functools.wraps` | 无内置 | 无直接对应 |
| 实例延迟属性 | `cached_property` | 私有字段 + getter | 懒加载字段模式 |

## 读代码

阶段项目 [`timing.py`](../../../examples/项目/13-计时重试装饰器/timing.py) 是本章装饰器的浓缩样板。先读 `timed`：它用 `perf_counter` 测耗时，用 `try/finally` 保证**即使函数抛异常也会打印耗时**——这是计时装饰器比“前后各一行 print”更稳妥的原因。

```python fragment
def timed(func: F) -> F:
    @functools.wraps(func)
    def wrapper(*args: object, **kwargs: object) -> object:
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            ms = (time.perf_counter() - start) * 1000
            print(f"{func.__name__} {ms:.2f} ms")
    return wrapper  # type: ignore[return-value]
```

读法 checklist：

1. **外层**接收被装饰函数 `func`，**内层** `wrapper` 才是调用时执行的对象。
2. `functools.wraps` 让 `wrapper` 对外看起来像 `func`（名称、文档字符串）。
3. `return wrapper  # type: ignore` 是类型检查器与“装饰器改变可调用类型”之间的折中；运行时不影响行为。
4. 同一文件里的 `retry` 使用**仅关键字参数** `*, times: int`，避免 `@retry(3)` 与 `@retry(times=3)` 混用时的歧义——读带参装饰器时先看外层签名。

`retry` 在 13.2 会逐行对照；本课只需把 `timed` 与 10.2 的 `timed` 模板联系起来。

## 练习

### 练习 1：partial 固定乘数

用 `functools.partial` 从 `mul(a, b)` 得到 `double(x) == mul(2, x)`。

```python exercise id=s13-l01-partial
# --- starter ---
import functools

def mul(a, b):
    return a * b
# --- solution ---
import functools

def mul(a, b):
    return a * b

double = functools.partial(mul, 2)
# --- check ---
assert double(5) == 10
assert double(0) == 0
```

### 练习 2：为昂贵纯函数加 cache

实现 `slugify(text: str) -> str`：去首尾空白、转小写、把空格换成 `-`。用 `@functools.cache` 装饰，保证相同字符串第二次调用命中缓存。

```python exercise id=s13-l01-cache
# --- starter ---
import functools

@functools.cache
def slugify(text: str) -> str:
    return text
# --- solution ---
import functools

@functools.cache
def slugify(text: str) -> str:
    t = text.strip().lower()
    return "-".join(t.split())
# --- check ---
assert slugify("  Hello  World ") == "hello-world"
info = slugify.cache_info()
assert info.hits == 0
slugify("  Hello  World ")
assert slugify.cache_info().hits >= 1
```


## 小结

- `partial` 生成“少几个参数”的调用；`lru_cache`/`cache` 适合昂贵、无副作用、参数可哈希的纯函数。
- 装饰器里几乎总是 `@functools.wraps(func)`，否则元信息丢失。
- 读 `timing.py` 的 `timed`：计时放在 `finally`，异常路径也会记录耗时。

## 延伸阅读

- [functools — 高阶函数与可调用对象操作](https://docs.python.org/zh-cn/3/library/functools.html)
- [术语：装饰器](https://docs.python.org/zh-cn/3/glossary.html#term-decorator)
- [10.2 装饰器](../10-读代码技巧/02-装饰器.md)
