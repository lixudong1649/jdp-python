---
title: 阶段 7 · 类与对象
goal: 读懂 class、self、属性与方法、属性链、特殊方法与 dataclass
---

# 阶段 7 · 类与对象

**达成标志**：读懂 SDK 风格代码中的对象创建、属性链和方法调用，如 `client.messages.create(...)`、`resp.content`、`block.type`。

| 课程 | 你将学会 |
|---|---|
| [7.1 类与实例](01-类与实例.md) | `class`、`__init__`、`self`、实例属性与类属性、方法、属性链 |
| [7.2 继承与特殊方法](02-继承与特殊方法.md) | 继承与 `super()`、`__repr__`/`__eq__`/`__len__`/`__call__` 等、`@property` |
| [7.3 dataclass 与枚举](03-dataclass与枚举.md) | `@dataclass`、`field`、`frozen`；`Enum`；SDK 响应模型的读法 |

**与终点的关系**：`anthropic.Anthropic(...)` 创建客户端对象；`client.messages.create(...)` 是属性链 + 方法调用；`resp.content` 中每个块都是带 `type`、`text`、`name`、`input`、`id` 属性的对象。
