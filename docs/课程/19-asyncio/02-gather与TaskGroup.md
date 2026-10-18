---
title: 19.2 gather 与 TaskGroup
---

# 19.2 gather 与 TaskGroup

> 前置：19.1 协程 · 约 25 分钟 · 官方对应：[TaskGroup](https://docs.python.org/zh-cn/3/library/asyncio-task.html#task-groups)（3.11 起）

## 目标

- 并发多个 await
- TaskGroup 结构化并发

## 核心概念

```python run
import asyncio
print(hasattr(asyncio, 'gather'))
```

## 易错点

- gather 默认 return_exceptions=False。
- TaskGroup 任一失败会取消其余。

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 本节重点 | 见官方文档 | — | — |

## 读代码

并行 tool call 时可 asyncio.gather 多个请求（若 SDK 支持 async）。

## 练习

```python exercise id=s19-l02-gather
# --- starter ---
import asyncio

gather = None
# --- solution ---
import asyncio

gather = asyncio.gather
# --- check ---
assert gather is asyncio.gather
```

## 小结

- gather 合并结果
- TaskGroup 3.11+

## 延伸阅读

- [asyncio Task](https://docs.python.org/zh-cn/3/library/asyncio-task.html)
