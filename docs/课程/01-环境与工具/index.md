---
title: 阶段 1 · 环境与工具
goal: 能用 uv 运行脚本、进入解释器；分清系统 Python 与项目环境
---

# 阶段 1 · 环境与工具

**达成标志**：能用 `uv run` 运行项目脚本、进入交互式解释器，知道依赖声明在哪里。

| 课程 | 你将学会 |
|---|---|
| [1.1 运行 Python 代码](01-运行Python代码.md) | 解释器、REPL、脚本三种运行方式；`sys.version` / `sys.executable` 判断“哪个 Python 在跑” |
| [1.2 uv 项目与依赖](02-uv项目与依赖.md) | `pyproject.toml`、`uv.lock`、`.venv` 的分工；`uv add` / `uv sync` / `uv run` |

**与终点的关系**：`minimal_agent.py` 依赖第三方包 `anthropic`、`python-dotenv`，必须在项目环境中用 `uv run examples/agent/minimal_agent.py` 运行。
