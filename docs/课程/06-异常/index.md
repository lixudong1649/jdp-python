---
title: 阶段 6 · 异常
goal: 读懂 Traceback 并定位出错行；读懂 try / except / raise 与 with
---

# 阶段 6 · 异常

**达成标志**：拿到一段 Traceback，能在 1 分钟内说出错误类型、原因和出错行；读懂错误处理与资源管理代码。

| 课程 | 你将学会 |
|---|---|
| [6.1 读懂 Traceback](01-读懂Traceback.md) | Traceback 的结构与阅读顺序；常见异常速查 |
| [6.2 try / except / raise](02-try-except-raise.md) | 捕获、`else`/`finally`、主动抛出、异常链、自定义异常、异常层次 |
| [6.3 with 与上下文管理器](03-with与上下文管理器.md) | `with` 的语义、`__enter__`/`__exit__`、`contextlib` |

**与终点的关系**：`LLM_PROVIDER` 写错时 `PROVIDERS[provider]` 抛 `KeyError`；网络或密钥问题时 SDK 抛出 `anthropic.APIError` 等异常。
