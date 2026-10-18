---
title: 阶段 19 · asyncio
goal: 读懂 SDK 的 async 接口并能写简单协程
layer: L4
---

# 阶段 19 · asyncio

**达成标志**：读懂 SDK 的 async 接口并能写简单协程。
阶段项目：[`examples/项目/19-异步minimal_agent/async_agent.py`](../../../examples/项目/19-异步minimal_agent/async_agent.py)（含 pytest）。

| 课程 | 你将学会 |
|---|---|
| [19.1 协程与事件循环](01-协程与事件循环.md) | 定义 async def 与 await |
| [19.2 gather 与 TaskGroup](02-gather与TaskGroup.md) | 并发多个 await |
| [19.3 异步 HTTP 概念](03-异步HTTP概念.md) | 理解 async 客户端与连接池 |

前置：完成 v1 阶段 1–11；本阶段属 **L4**（核对日期 2026-10-18，正文对 Python 3.12–3.15 成立，项目固定 3.12）。
