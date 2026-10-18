---
title: 13.3 contextlib 上下文管理器
---

# 13.3 contextlib 上下文管理器

> 前置：6.3 with 与上下文管理器 · 约 25 分钟 · 官方对应：[contextlib](https://docs.python.org/zh-cn/3/library/contextlib.html)

## 目标

- 用 `@contextmanager` 写 with 块
- 理解 yield 前后是 setup/teardown

## 核心概念

```python run
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
```

## 易错点

- `yield` 只能出现一次。
- 忘记 finally 会导致资源泄漏。

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 本节重点 | 见官方文档 | — | — |

## 读代码

`with client:` 或 SDK 提供的上下文管理器，读 `__enter__/__exit__` 或 `@contextmanager`。

## 练习

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

## 小结

- contextmanager 生成器变 with
- finally 保证清理

## 延伸阅读

- [contextlib](https://docs.python.org/zh-cn/3/library/contextlib.html)
