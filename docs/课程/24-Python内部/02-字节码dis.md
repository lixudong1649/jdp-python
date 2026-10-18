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
def bytecode_name(opname: str) -> str:
    return ""
# --- solution ---
def bytecode_name(opname: str) -> str:
    return opname.upper()
# --- check ---
assert bytecode_name("load_const") == "LOAD_CONST"
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
