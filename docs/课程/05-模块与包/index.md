---
title: 阶段 5 · 模块与包
goal: 读懂各种 import 写法，判断名字来自内置、标准库、第三方还是本地
---

# 阶段 5 · 模块与包

**达成标志**：看到任意 `import` 语句，能说出导入了什么、名字从哪里来、需要哪个依赖。

| 课程 | 你将学会 |
|---|---|
| [5.1 模块与 import](01-模块与import.md) | 模块即文件；`import` 的四种写法；模块搜索路径；`if __name__ == "__main__"` |
| [5.2 包与项目结构](02-包与项目结构.md) | 包与 `__init__.py`；相对导入；`python -m`；src 布局；循环导入 |

**与终点的关系**：`minimal_agent.py` 开头的 `import os`、`import anthropic`、`from dotenv import load_dotenv` 分别来自标准库和两个第三方包。
