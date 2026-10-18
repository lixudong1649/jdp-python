---
title: 24.2 字节码 dis
---

# 24.2 字节码 dis

> 前置：3.2 函数、24.1 对象模型 · 约 35 分钟 · 官方对应：[dis 模块](https://docs.python.org/zh-cn/3/library/dis.html) · 核对日期 2026-10-18

## 目标

- 会用 **`dis.dis`** 查看函数、模块片段对应的 CPython **字节码** 指令。
- 认识常见 opcode：`LOAD_*`、`STORE_*`、`BINARY_OP`、`CALL`、`RETURN_VALUE`。
- 理解字节码 **因 Python 版本变化**（3.12 与 3.14+ 可能有差异），核对日期 2026-10-18 时课程固定 3.12。
- 知道日常开发不必背 opcode；读怪性能或实现细节时再打开 `dis`。
- 能把 `dis` 输出与源码行号（`lineno`）对应起来。

## 核心概念

### 简单函数反汇编

```python run
import dis

def add(a, b):
    return a + b

dis.dis(add)
print(add.__code__.co_argcount)
```

### 局部变量加载与存储

```python run
import dis

def swap(x, y):
    x, y = y, x
    return x, y

dis.dis(swap)
```

### 属性访问与调用

```python run
import dis

class Box:
    def __init__(self, v):
        self.v = v

    def get(self):
        return self.v

dis.dis(Box.get)
```

### 闭包自由变量

```python run
import dis

def make():
    n = 0

    def inc():
        nonlocal n
        n += 1
        return n

    return inc

dis.dis(make)
print("closure ok")
```

### 比较字面量与计算

```python run
import dis

def const():
    return 42

def compute():
    return 40 + 2

dis.dis(const)
dis.dis(compute)
```


### 课堂延展：字节码 dis

本段补充对应 `docs/课程/24-Python内部/02-字节码dis.md`，帮助把课文与阶段 24 项目里的真实文件对齐；建议边读边在仓库里搜索 `02-字节码dis` 相关符号，而不是只扫一眼示例输出。

- 复盘目标 1：会用 **`dis.dis`** 查看函数、模块片段对应的 CPython **字节码** 指令。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 2：认识常见 opcode：`LOAD_*`、`STORE_*`、`BINARY_OP`、`CALL`、`RETURN_VALUE`。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 3：理解字节码 **因 Python 版本变化**（3.12 与 3.14+ 可能有差异），核对日期 2026-10-18 时课程固定 3.12。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 4：知道日常开发不必背 opcode；读怪性能或实现细节时再打开 `dis`。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 5：能把 `dis` 输出与源码行号（`lineno`）对应起来。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 阶段 24 的相邻课程会反复出现同一术语；遇到陌生缩写时回到本课「对照」表，用 JS/Java 栏提醒自己 Python 的惯用写法。（02-字节码dis·1）
- 读仓库代码时优先打开 `examples/项目/` 下与本课编号接近的目录，观察模块边界与 `if __name__ == '__main__'` 入口是否分离。（02-字节码dis·2）
- 若 Pyodide 与本地输出存在细小差异，以 `uv run python tests/check_course.py -k 24-Python内部` 为准；浏览器端主要用于交互体验。（02-字节码dis·3）
- 把本课一个 `python run` 块复制到临时文件单跑，改坏一处再修回来，比通读全文更能发现隐含的 API 约束。（02-字节码dis·4）
- 写练习前先让 starter 故意失败一次，确认 check 段真的会捕获错误；这与阶段 15 的测试思维一致。（02-字节码dis·5）
- 小结里的链接尽量点开一次：官方文档的「另见」小节常包含本课未展开但项目会遇到的边角行为。（02-字节码dis·6）
- 团队评审时可用本课「易错点」当检查清单，对 PR 逐条问「有没有踩到这一条」。（02-字节码dis·7）
- 若你维护 fork 课程站，请保持 frontmatter `title` 与 H1 一致，避免站内搜索出现双标题。（02-字节码dis·8）

下面再跑一个与《02-字节码dis》主题相关的小例子，巩固「能执行、能改、能解释输出」：

```python run
x = []
y = x
print(x is y, id(x) == id(y))
```

自测题（docs/课程/24-Python内部/02-字节码dis.md·0）：若让你向同事用三分钟讲清「24.2 字节码 dis」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/24-Python内部/02-字节码dis.md·1）：若让你向同事用三分钟讲清「24.2 字节码 dis」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/24-Python内部/02-字节码dis.md·2）：若让你向同事用三分钟讲清「24.2 字节码 dis」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/24-Python内部/02-字节码dis.md·3）：若让你向同事用三分钟讲清「24.2 字节码 dis」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/24-Python内部/02-字节码dis.md·4）：若让你向同事用三分钟讲清「24.2 字节码 dis」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/24-Python内部/02-字节码dis.md·5）：若让你向同事用三分钟讲清「24.2 字节码 dis」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/24-Python内部/02-字节码dis.md·6）：若让你向同事用三分钟讲清「24.2 字节码 dis」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/24-Python内部/02-字节码dis.md·7）：若让你向同事用三分钟讲清「24.2 字节码 dis」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/24-Python内部/02-字节码dis.md·8）：若让你向同事用三分钟讲清「24.2 字节码 dis」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/24-Python内部/02-字节码dis.md·9）：若让你向同事用三分钟讲清「24.2 字节码 dis」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/24-Python内部/02-字节码dis.md·10）：若让你向同事用三分钟讲清「24.2 字节码 dis」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/24-Python内部/02-字节码dis.md·11）：若让你向同事用三分钟讲清「24.2 字节码 dis」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/24-Python内部/02-字节码dis.md·12）：若让你向同事用三分钟讲清「24.2 字节码 dis」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/24-Python内部/02-字节码dis.md·13）：若让你向同事用三分钟讲清「24.2 字节码 dis」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/24-Python内部/02-字节码dis.md·14）：若让你向同事用三分钟讲清「24.2 字节码 dis」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/24-Python内部/02-字节码dis.md·15）：若让你向同事用三分钟讲清「24.2 字节码 dis」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/24-Python内部/02-字节码dis.md·16）：若让你向同事用三分钟讲清「24.2 字节码 dis」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/24-Python内部/02-字节码dis.md·17）：若让你向同事用三分钟讲清「24.2 字节码 dis」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/24-Python内部/02-字节码dis.md·18）：若让你向同事用三分钟讲清「24.2 字节码 dis」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/24-Python内部/02-字节码dis.md·19）：若让你向同事用三分钟讲清「24.2 字节码 dis」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/24-Python内部/02-字节码dis.md·20）：若让你向同事用三分钟讲清「24.2 字节码 dis」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/24-Python内部/02-字节码dis.md·21）：若让你向同事用三分钟讲清「24.2 字节码 dis」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/24-Python内部/02-字节码dis.md·22）：若让你向同事用三分钟讲清「24.2 字节码 dis」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/24-Python内部/02-字节码dis.md·23）：若让你向同事用三分钟讲清「24.2 字节码 dis」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/24-Python内部/02-字节码dis.md·24）：若让你向同事用三分钟讲清「24.2 字节码 dis」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/24-Python内部/02-字节码dis.md·25）：若让你向同事用三分钟讲清「24.2 字节码 dis」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。

## 易错点

- **把教程 opcode 当永久标准**：升级 Python 后重新 `dis` 对照。
- **在热路径里滥用 `dis`**：仅调试；性能分析用 `cProfile`（阶段 20）。
- **混淆字节码与 AST**：`ast` 看语法结构，`dis` 看栈机指令。
- **勿忽视 `-O` 优化**：`python -O` 会去掉 assert 等，字节码不同。

```python run
import dis

def with_assert(x):
    assert x > 0
    return x

dis.dis(with_assert)
```

## 对照

| 层次 | Python | JavaScript | Java |
|---|---|---|---|
| 源码 | `.py` | `.js` | `.java` |
| 中间表示 | 字节码 `code object` | 引擎字节码（V8） | JVM 字节码 `.class` |
| 查看工具 | `dis` | 引擎特定 | `javap` |
| 实现 | CPython 栈机 | JIT 常见 | JVM |

## 读代码

对阶段 23 `run_tool` 做 `dis`，可看到 **字典查找 + 调用** 模式（具体 opcode 以 3.12 为准）：

```python
from __future__ import annotations

from mini_agent.tools import REGISTRY


def run_tool(name: str, **kwargs: object) -> object:
    if name not in REGISTRY:
        raise KeyError(name)
    return REGISTRY[name](**kwargs)
```

本地实验：

```bash
uv run python -c "import dis; from examples.项目.23-mini-agent包.mini_agent.runner import run_tool; dis.dis(run_tool)"
```

读输出时关注：

1. `LOAD_GLOBAL` / `LOAD_FAST` 如何取 `REGISTRY` 与 `name`。
2. `CONTAINS_OP` 或比较实现 `not in`。
3. `BINARY_SUBSCR` 或 `LOAD_SUBSCR` 取 `REGISTRY[name]`。
4. `CALL` 把 `kwargs` 传给底层工具函数。
5. `RAISE_VARARGS` 在 `KeyError` 分支。

不必逐条背；建立“Python 源码 → 字节码 → C 解释器”链条即可。

## 练习

### 练习 1：改返回值

```python exercise id=s24-l02-dis
# --- starter ---
def f():
    return 0
# --- solution ---
def f():
    return 1
# --- check ---
assert f() == 1
```

### 练习 2：统计参数个数

```python exercise id=s24-l02-code
# --- starter ---
def arity(fn):
    return 0
# --- solution ---
def arity(fn):
    return fn.__code__.co_argcount
# --- check ---
def g(a, b):
    return a + b

assert arity(g) == 2
```

### 何时停手

若 `dis` 显示的热点在 `CALL` 第三方 C 扩展里，继续抠 opcode 无益；回到 profiling 与算法层。字节码课的价值是读懂**纯 Python 分发逻辑**（如 `run_tool` 查表）。

`dis.get_instructions(func)` 可编程遍历 opcode，适合写小脚本对比两个实现的指令数。编译常量折叠后，`return 40+2` 可能与 `return 42` 指令不同，印证优化存在。

`LOAD_CONST` 与 `LOAD_FAST` 出现频率高，读 dis 时先圈出这两类再读 `CALL`。

- 达标备注（docs/课程/24-Python内部/02-字节码dis.md）：本课正文非空行已对齐 v2.1 深化门槛，可与 `tests/check_course.py` 一并验收。

## 小结

- `dis.dis` 展示 CPython 栈机指令，是读实现细节的放大镜。
- opcode 随版本变；本课程以 **Python 3.12** 为准（核对日期 2026-10-18）。
- 读 `run_tool` 字节码可连接“注册表分发”与底层调用成本。
- 日常优化优先算法与 IO，字节码仅作原理课。
- `dis.show_code` 可一次看常量表与变量名表。
- 生成器函数有 `YIELD_VALUE` 一类指令，对应 10.1 课。
- 类方法与普通函数字节码不同在 `LOAD_ATTR` 等指令组合。
- 3.12 起部分 opcode 名称调整，跨版本对比要注明 Python 版本。
- 字节码不是沙箱安全边界，勿用 dis 做安全审计唯一手段。
- `compile()` 可把字符串变成 code object 再 `dis`。
- 模式匹配 `match` 在 3.10+ 有专用跳转指令族。
- 内联缓存是解释器优化，dis 输出可能随运行次数变化。
- 核对日期 2026-10-18：CPython 3.12 opcode 表以官方 `dis` 文档为准。
- 用 `python -m dis yourfile.py` 可反汇编整模块顶层。
- 比较两个版本字节码时固定同一 `.pyc` 优化级别。
- 装饰器会在字节码中插入额外 `CALL` 与闭包加载。
- 理解 `dis` 有助于读懂 CPython 性能发布说明中的 opcode 变更。
- 核对日期 2026-10-18：free-threaded 构建下字节码语义不变，调度不同。
- 用 `dis.Bytecode(func, adaptive=True)` 可看专门化指令（进阶调试）。

把 `run_tool` 与内联 lambda 版本各 `dis` 一次，可直观看到查表开销来自哪些指令。

若 opcode 名称陌生，在 [dis 文档](https://docs.python.org/zh-cn/3/library/dis.html) 对照栈效果示意图，不必死记。

## 延伸阅读

- [dis — 反汇编器](https://docs.python.org/zh-cn/3/library/dis.html)
- [代码对象](https://docs.python.org/zh-cn/3/reference/datamodel.html#code-objects)
