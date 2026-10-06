# Python 概览与环境

本文回答两个问题：Python 是什么；在本项目里如何准备和使用 Python 环境。学习顺序见 [学习路线](学习路线.md)。

> 信息核对日期：2026-10-06。版本信息以 [python.org 下载页](https://www.python.org/downloads/) 与 [版本状态页](https://devguide.python.org/versions/) 为准。

## 1. Python 是什么

| 特点 | 含义 | 读代码时的影响 |
|---|---|---|
| 解释执行 | 由解释器（CPython）逐条执行源码，无需手动编译 | `python xxx.py` 或 `uv run xxx.py` 即可运行 |
| 动态类型 | 变量不声明类型，类型属于“值”而不是“变量” | 需从赋值和用法推断类型；类型注解只是提示 |
| 强类型 | 不同类型不会被隐式混用，如 `"1" + 1` 会报错 | 报错信息 `TypeError` 很常见 |
| 缩进即语法 | 用缩进（通常 4 个空格）表示代码块，而不是 `{}` | 看缩进就能看出 `if`/`for`/`def` 的范围 |
| 一切皆对象 | 数字、字符串、函数、模块都是对象，有属性和方法 | `obj.attr`、`obj.method()` 随处可见 |
| “自带电池” | 标准库覆盖文件、网络、JSON、日期等常见需求 | 先查标准库，再找第三方包 |

设计哲学见 [PEP 20 – Python 之禅](https://peps.python.org/pep-0020/)（在解释器中执行 `import this` 也可查看）；代码风格见 [PEP 8](https://peps.python.org/pep-0008/)。

## 2. 版本现状

| 版本 | 状态 | 支持截止 | 说明 |
|---|---|---|---|
| 3.15 | 预发布 | 2031-10 | 正式版计划于 2026-10-09 发布（[PEP 790](https://peps.python.org/pep-0790/)） |
| **3.14** | **bugfix（最新稳定版 3.14.8，2026-09-30）** | 2030-10 | 新项目首选；[3.14 新特性](https://docs.python.org/zh-cn/3/whatsnew/3.14.html)、[PEP 745](https://peps.python.org/pep-0745/) |
| 3.13 | security | 2029-10 | 3.13.16 为最后一个常规维护版 |
| 3.12 | security | 2028-10 | **本项目当前固定版本**（`.python-version`），本机已安装 |
| 3.11 | security | 2027-10 | — |
| 3.10 | 已停止支持 | 2026-10 | 不再接收安全更新，应升级 |

入门阶段 3.12 与 3.14 的语法差异几乎不影响学习。需要升级时：`uv python install 3.14 && uv python pin 3.14`。

## 3. 环境核心概念

| 概念 | 是什么 | 本项目中的文件 |
|---|---|---|
| 解释器 | 运行 Python 代码的程序 | 由 `uv` 按 `.python-version` 选择 |
| 虚拟环境（venv） | 每个项目独立的解释器 + 第三方包目录，避免项目间依赖冲突 | `.venv/`（git 忽略） |
| 包 / PyPI | 第三方库及其官方仓库 [pypi.org](https://pypi.org/) | — |
| `pyproject.toml` | 项目元数据与依赖声明的标准文件（[PEP 621](https://peps.python.org/pep-0621/)） | `pyproject.toml` |
| 锁文件 | 记录依赖的精确版本，保证可复现 | `uv.lock`（由 uv 生成，勿手改） |
| 环境变量 / `.env` | 存放密钥等本地配置，不写进代码 | `.env`（git 忽略）、`.env.example`（模板） |

官方资料：[venv 模块](https://docs.python.org/zh-cn/3/library/venv.html)、[安装包教程（packaging.python.org）](https://packaging.python.org/en/latest/tutorials/installing-packages/)、[编写 pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)。

## 4. uv：本项目的环境与依赖工具

[uv](https://docs.astral.sh/uv/) 一个工具统一了 Python 版本管理、虚拟环境、依赖安装与运行，替代 `pyenv` + `venv` + `pip` 的组合。本项目约定：**依赖只通过 uv 管理，运行一律用 `uv run`**。

| 场景 | 命令 |
|---|---|
| 同步环境（按 `uv.lock` 创建 `.venv` 并安装依赖） | `uv sync` |
| 运行脚本（自动同步后在 `.venv` 中执行） | `uv run examples/agent/minimal_agent.py` |
| 进入交互式解释器 | `uv run python` |
| 添加 / 移除依赖（同时更新 `pyproject.toml` 与 `uv.lock`） | `uv add <包名>` / `uv remove <包名>` |
| 查看已安装 / 可用的 Python 版本 | `uv python list` |
| 安装并固定 Python 版本 | `uv python install 3.14` / `uv python pin 3.14` |
| 新建项目 | `uv init <目录>` |

官方指南：[项目工作流](https://docs.astral.sh/uv/guides/projects/)、[运行脚本](https://docs.astral.sh/uv/guides/scripts/)、[管理依赖](https://docs.astral.sh/uv/concepts/projects/dependencies/)。

## 5. 常见问题

- **`ModuleNotFoundError`**：多半是没在项目环境里运行。用 `uv run`，而不是系统的 `python3`。
- **`python3 --version` 与项目版本不一致**：正常。系统解释器与项目解释器相互独立，以 `uv run python --version` 为准。
- **密钥放哪里**：只放 `.env`，代码里用 `os.getenv("变量名")` 读取；不要写进代码、文档或日志。
