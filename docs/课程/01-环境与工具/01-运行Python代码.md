---
title: 1.1 运行 Python 代码
---

# 1.1 运行 Python 代码

> 前置：无 · 约 20 分钟 · 官方对应：[使用 Python 解释器](https://docs.python.org/zh-cn/3/tutorial/interpreter.html) · 核对日期 2026-10-06

## 目标

- 说清“解释器”“脚本”“交互式解释器（REPL）”三者的关系。
- 用 `uv run` 在项目环境中运行脚本和 REPL。
- 用 `sys.version`、`sys.executable` 判断当前是哪个 Python 在运行。

## 核心概念

### 解释器与三种运行方式

Python 源码由**解释器**执行。官方解释器叫 CPython（C 语言实现），`python3` 命令就是它。源码先被编译为字节码，再由解释器的虚拟机执行，这一步是自动的，不需要手动编译。

| 方式 | 命令（本项目） | 适用 |
|---|---|---|
| 运行脚本 | `uv run examples/agent/minimal_agent.py` | 正式运行一个 `.py` 文件 |
| 交互式解释器（REPL） | `uv run python` | 试验一两行代码、查看对象 |
| 运行模块 | `uv run python -m json.tool data.json` | 以模块名运行（标准库工具、包内入口） |

REPL 中的提示符 `>>>` 表示等待输入，`...` 表示续行；直接输入表达式会回显其值。官方文档中的示例常写成这种形式：

```pycon
>>> 2 + 3
5
>>> name = "Python"
>>> name.upper()
'PYTHON'
```

退出 REPL：输入 `exit()` 或按 `Ctrl-D`（Windows 为 `Ctrl-Z` 回车）。Python 3.13 起默认的新 REPL 支持多行编辑、彩色提示，3.14 起增加语法高亮（核对日期 2026-10-06）。

### 本站的代码块

带“Python · 可运行”标记的代码块可以直接点 **▶ 运行**，也可以点“编辑”修改后再运行。它们运行在浏览器里的 Pyodide（编译为 WebAssembly 的 CPython）中，与本地 Python 行为基本一致；不同点是浏览器中不能安装任意第三方包、不能访问你电脑的文件和网络。

```python run
print("Hello, Python")
print(1 + 2, "个参数可以一起打印")
```

### 哪个 Python 在运行

同一台机器上常有多个解释器：系统自带的、官网安装的、uv 为项目下载的。`sys` 模块告诉你当前进程用的是哪个：

```python run
import sys

print(sys.version)      # 版本号与构建信息
print(sys.version_info >= (3, 12))  # 元组比较：判断最低版本
print(sys.executable)   # 解释器可执行文件路径（浏览器中可能为空字符串）
```

在本项目里，`uv run python -c "import sys; print(sys.executable)"` 会输出一个以 `.venv/bin/python` 结尾的路径，而系统的 `python3` 输出的是另一个路径。**以项目环境为准**：依赖只装在 `.venv` 中。

### 脚本就是从上到下执行的语句

一个 `.py` 文件从第一行执行到最后一行；`def` 只是定义函数，调用时才执行函数体。

```python run
print("1. 文件开始执行")

def greet(name):
    print(f"3. 你好，{name}")

print("2. 定义完函数，还没调用")
greet("开发者")
```

## 易错点

- **用错解释器**：直接 `python3 examples/agent/minimal_agent.py` 通常会报 `ModuleNotFoundError: No module named 'anthropic'`，因为系统 Python 里没有项目依赖。用 `uv run`。
- **在 REPL 里粘贴脚本**：REPL 中缩进块结束后需要一个空行；整段脚本更适合保存成文件运行。
- **把 `>>>` 一起复制**：官方文档示例中的 `>>>`、`...` 是提示符，不是代码。
- **缩进混用 Tab 与空格**：会触发 `TabError`。统一用 4 个空格（[PEP 8](https://peps.python.org/pep-0008/)）。

```python run raises=IndentationError
def f():
print("函数体必须缩进")
```

## 对照

| 概念 | Python | JS（Node） | Java |
|---|---|---|---|
| 运行脚本 | `python app.py` | `node app.js` | `java App.java`（单文件）/ 先 `javac` |
| 交互式环境 | `python`（REPL） | `node`（REPL） | `jshell` |
| 项目内运行 | `uv run app.py` | `npx` / `npm run` | `mvn exec:java` / `gradle run` |
| 代码块 | 缩进 | `{}` | `{}` |

## 读代码

`minimal_agent.py` 顶部的文档字符串直接写明了运行方式：

```python
"""最小 Agent 循环示例（Anthropic Messages API 工具调用）。
...
运行（在项目根目录）：uv run examples/agent/minimal_agent.py
"""
```

读任何陌生脚本，**先看文件头的文档字符串和 README 中的运行命令**，再看 `import`。很多脚本还会检查版本，例如：

```python
import sys

if sys.version_info < (3, 12):
    raise SystemExit("需要 Python 3.12 或更高版本")
```

## 练习

### 练习 1：版本判断

实现 `is_supported(version_info)`：当传入的版本元组不低于 `(3, 12)` 时返回 `True`，否则返回 `False`。提示：元组可以直接比较大小，按元素从左到右逐个比较。

```python exercise id=s01-l01-version
# --- starter ---
def is_supported(version_info):
    # 在这里写你的代码
    ...
# --- solution ---
def is_supported(version_info):
    return tuple(version_info[:2]) >= (3, 12)
# --- check ---
assert is_supported((3, 12, 0)) is True, "3.12.0 应受支持"
assert is_supported((3, 14, 8)) is True, "3.14.8 应受支持"
assert is_supported((3, 11, 9)) is False, "3.11 不应受支持"
assert is_supported((2, 7, 18)) is False, "2.7 不应受支持"
import sys
assert is_supported(sys.version_info) is True, "当前运行环境应受支持"
```

### 练习 2：执行顺序

不运行代码，先写出 `order` 列表最终的值，再赋给 `answer`，提交检查。

```python exercise id=s01-l01-order
# --- starter ---
order = []
order.append("a")

def f():
    order.append("c")

order.append("b")
f()

answer = []  # 写出 order 的最终值，例如 ["x", "y"]
# --- solution ---
order = []
order.append("a")

def f():
    order.append("c")

order.append("b")
f()

answer = ["a", "b", "c"]
# --- check ---
assert answer == order, f"answer 应为 {order}"
```

## 小结

- 解释器执行源码；脚本从上到下执行，`def` 只定义不执行。
- 本项目一律用 `uv run` 运行，保证使用 `.venv` 中的解释器与依赖。
- `sys.version_info` 判断版本，`sys.executable` 判断解释器位置。
- 读陌生脚本先看文档字符串与运行命令。

## 延伸阅读

- [使用 Python 解释器](https://docs.python.org/zh-cn/3/tutorial/interpreter.html)
- [命令行与环境](https://docs.python.org/zh-cn/3/using/cmdline.html)
- [sys 模块](https://docs.python.org/zh-cn/3/library/sys.html)
- [uv：运行脚本](https://docs.astral.sh/uv/guides/scripts/)
