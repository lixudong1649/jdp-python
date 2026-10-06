---
title: 阶段 3 · 控制流与函数
goal: 读懂 if / for / while / def；关键字参数、*args/**kwargs 与 ** 解包；函数是对象
---

# 阶段 3 · 控制流与函数

**达成标志**：能说出程序“走哪条路、重复几次、把什么封装成函数”，并读懂任意函数签名与调用。

| 课程 | 你将学会 |
|---|---|
| [3.1 条件与循环](01-条件与循环.md) | `if/elif/else`、条件表达式、`for` 与 `range`/`enumerate`/`zip`、`while`、`break`/`continue`、循环的 `else`、`match` |
| [3.2 函数定义与调用](02-函数定义与调用.md) | `def`/`return`、位置与关键字参数、默认值、可变默认值陷阱、函数是对象 |
| [3.3 参数进阶与解包](03-参数进阶与解包.md) | `*args`/`**kwargs`、仅限关键字 `*`、仅限位置 `/`、调用时的 `*` 与 `**` 解包 |
| [3.4 作用域、闭包与 lambda](04-作用域闭包与lambda.md) | LEGB 规则、`global`/`nonlocal`、闭包、`lambda` 与 `sorted(key=...)` |

**与终点的关系**：`minimal_agent.py` 的主循环 `for turn in range(1, MAX_TURNS + 1): ... else: ...` 和核心一行 `TOOL_FUNCTIONS[block.name](**block.input)` 都在本阶段讲清。
