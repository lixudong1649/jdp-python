---
title: 13.1 functools 入门
---

# 13.1 functools 入门

> 前置：10.2 装饰器 · 约 25 分钟 · 官方对应：[functools](https://docs.python.org/zh-cn/3/library/functools.html)

## 目标

- 会用 partial 固定参数
- 会用 lru_cache 做纯函数缓存
- 会用 wraps 保留元信息

## 核心概念

```python run
import functools

@functools.lru_cache(maxsize=32)
def fib(n: int) -> int:
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

print(fib(10), fib.cache_info().hits)
```

## 易错点

- `lru_cache` 要求参数可哈希。
- 忘记 `@wraps` 导致 `help(fn)` 显示 wrapper。

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 本节重点 | 见官方文档 | — | — |

## 读代码

读装饰器源码时常见 `functools.wraps`；SDK 中间层也会缓存只读查询。

## 练习

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
```

## 小结

- partial 预先绑定参数
- lru_cache 适合昂贵纯函数

## 延伸阅读

- [functools](https://docs.python.org/zh-cn/3/library/functools.html)
