---
title: 阶段 9 · 类型注解
goal: '读懂 def f(x: int) -> str、X | None、泛型、TypedDict、Literal、Protocol'
---

# 阶段 9 · 类型注解

**达成标志**：读懂现代 Python 代码与 SDK 中的类型注解，知道它们在运行时不做检查。

| 课程 | 你将学会 |
|---|---|
| [9.1 类型注解基础](01-类型注解基础.md) | 参数/返回值/变量注解、内置泛型、`X \| None`、`Any`、运行时行为 |
| [9.2 typing 进阶](02-typing进阶.md) | `Literal`、`TypedDict`、`Callable`、`Protocol`、泛型与 3.12 新语法、`overload`、`TYPE_CHECKING` |

**与终点的关系**：`minimal_agent.py` 没有写注解，但它调用的 `anthropic` SDK 每个签名都有完整注解；读懂注解才能读懂 `create(...)` 接受什么、返回什么。
