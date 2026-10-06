---
title: 3.4 作用域、闭包与 lambda
---

# 3.4 作用域、闭包与 lambda

> 前置：3.3 · 约 30 分钟 · 官方对应：[Python 作用域和命名空间](https://docs.python.org/zh-cn/3/tutorial/classes.html#python-scopes-and-namespaces)、[Lambda 表达式](https://docs.python.org/zh-cn/3/tutorial/controlflow.html#lambda-expressions)

## 目标

- 用 LEGB 规则判断一个名字从哪里来。
- 读懂 `global`、`nonlocal`，知道它们为何少见。
- 理解闭包：内部函数“记住”外部变量（装饰器的基础）。
- 读懂 `lambda` 以及 `sorted(key=...)`、`max(key=...)` 的用法。

## 核心概念

### LEGB：名字查找顺序

读取一个名字时，按以下顺序查找，找到即停：

| 层 | 含义 | 例子 |
|---|---|---|
| **L**ocal | 当前函数内部 | 参数、函数内赋值的变量 |
| **E**nclosing | 外层函数（嵌套函数时） | 闭包捕获的变量 |
| **G**lobal | 当前模块顶层 | `MAX_TURNS`、`TOOL_FUNCTIONS` |
| **B**uilt-in | 内置名字 | `print`、`len`、`range` |

```python run
MAX_TURNS = 5              # 全局

def outer():
    prefix = "[agent]"     # outer 的局部，对 inner 来说是 Enclosing
    def inner(turn):       # turn 是 inner 的局部
        return f"{prefix} 第 {turn}/{MAX_TURNS} 轮，len={len('abc')}"   # len 来自内置
    return inner(1)

print(outer())
```

只有**函数**（以及类、推导式）会创建新作用域；`if`、`for`、`while` 块不会——循环结束后循环变量仍然可用：

```python run
for turn in range(1, 4):
    pass
print(turn)   # 3：for 不创建作用域
```

### 赋值决定局部：global 与 nonlocal

**在函数内对一个名字赋值，会让它成为该函数的局部变量**（整个函数体内都是）。想在函数内修改全局或外层变量，需要声明：

```python run
counter = 0

def increment():
    global counter      # 声明：这里的 counter 指模块级变量
    counter += 1

increment(); increment()
print(counter)

def make_counter():
    count = 0
    def step():
        nonlocal count  # 声明：指外层函数的 count
        count += 1
        return count
    return step

c = make_counter()
print(c(), c(), c())
```

工程代码中很少用 `global`：可变的全局状态难以追踪。修改**可变对象的内容**（如 `messages.append(...)`）不是重新赋值，不需要声明。

### 闭包

内部函数引用了外层函数的变量，并且在外层函数返回后仍可使用——这个“函数 + 被捕获的变量”就是闭包。

```python run
def make_greeter(greeting):
    def greet(name):
        return f"{greeting}，{name}"
    return greet           # 返回函数对象，不调用

hello = make_greeter("你好")
hi = make_greeter("Hi")
print(hello("Python"), "|", hi("Python"))
print(hello.__closure__[0].cell_contents)   # 被捕获的值
```

### lambda

`lambda 参数: 表达式` 创建一个匿名函数，只能包含**一个表达式**（自动返回其值）。最常见的用途是作为 `key=` 参数：

```python run
blocks = [
    {"type": "text", "len": 30},
    {"type": "tool_use", "len": 5},
    {"type": "thinking", "len": 120},
]
print(sorted(blocks, key=lambda b: b["len"]))               # 按长度升序
print(max(blocks, key=lambda b: b["len"])["type"])          # 最长的块
print(sorted(["Banana", "apple", "cherry"], key=str.lower))  # key 也可以是普通函数

square = lambda x: x * x   # 能工作，但 PEP 8 建议给函数起名时用 def
print(square(4))
```

## 易错点

- **`UnboundLocalError`**：函数内先读后赋同一个名字。因为赋值让它成为局部变量，读取时局部变量还没有值。
- **循环中创建闭包**：闭包捕获的是**变量**而不是当时的值，循环结束后所有闭包看到的都是最后一个值。用默认参数 `lambda i=i: i` 固定当前值。
- **把复杂逻辑塞进 lambda**：超过一行就改用 `def`。

```python run raises=UnboundLocalError
total = 0

def add(n):
    total = total + n   # 赋值使 total 成为局部变量，右侧读取时它还没有值
    return total

add(1)
```

```python run
funcs = [lambda: i for i in range(3)]
print([f() for f in funcs])          # [2, 2, 2]
funcs = [lambda i=i: i for i in range(3)]
print([f() for f in funcs])          # [0, 1, 2]
```

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 块作用域 | 无（只有函数级） | `let`/`const` 有块作用域 | 有块作用域 |
| 修改外层变量 | 需 `nonlocal` / `global` | 直接修改 | lambda 只能捕获 effectively final 变量 |
| 匿名函数 | `lambda x: x * 2`（单表达式） | `x => x * 2`（可多语句） | `x -> x * 2` |
| 排序键 | `sorted(xs, key=f)` | `xs.sort((a, b) => …)` 比较器 | `Comparator.comparing(f)` |

## 读代码

`minimal_agent.py` 是一个模块级脚本：`client`、`tools`、`messages`、`TOOL_FUNCTIONS` 都是**全局**名字；`get_weather` 内部的 `city` 是局部名字。循环里 `messages.append(...)` 修改的是列表对象内容，不是给 `messages` 重新赋值，所以无需 `global`。

真实代码中常见的闭包与 lambda：

```python
handlers = {
    "text": lambda block: block.text,
    "tool_use": lambda block: f"调用 {block.name}",
}
latest = max(runs, key=lambda r: r.created_at)
```

## 练习

### 练习 1：计数器工厂

实现 `make_counter(start=0)`，返回一个函数；每次调用该函数返回递增后的计数。不同计数器互不影响。

```python exercise id=s03-l04-counter
# --- starter ---
def make_counter(start=0):
    def step():
        ...
    return step
# --- solution ---
def make_counter(start=0):
    count = start
    def step():
        nonlocal count
        count += 1
        return count
    return step
# --- check ---
a = make_counter()
b = make_counter(10)
assert [a(), a(), a()] == [1, 2, 3]
assert b() == 11, "b 应从 10 开始独立计数"
assert a() == 4
```

### 练习 2：按键排序

实现 `sort_tools(tools)`：按 `name` 字母序（不区分大小写）返回新列表；实现 `longest_description(tools)`：返回 `description` 最长的工具的 `name`。使用 `key=lambda ...`。

```python exercise id=s03-l04-sort
# --- starter ---
def sort_tools(tools):
    return tools

def longest_description(tools):
    ...
# --- solution ---
def sort_tools(tools):
    return sorted(tools, key=lambda t: t["name"].lower())

def longest_description(tools):
    return max(tools, key=lambda t: len(t["description"]))["name"]
# --- check ---
tools = [
    {"name": "get_weather", "description": "查询城市天气"},
    {"name": "Calc", "description": "计算"},
    {"name": "browse", "description": "打开网页并返回正文内容"},
]
assert [t["name"] for t in sort_tools(tools)] == ["browse", "Calc", "get_weather"]
assert tools[0]["name"] == "get_weather", "不要修改原列表（用 sorted 返回新列表）"
assert longest_description(tools) == "browse"
```

## 小结

- 名字按 Local → Enclosing → Global → Built-in 查找；只有函数等创建作用域。
- 函数内赋值即局部；修改外层名字需 `nonlocal` / `global`，修改对象内容不需要。
- 闭包 = 函数 + 捕获的外层变量，是装饰器的基础。
- `lambda` 只写单个表达式，主要用于 `key=`。

## 延伸阅读

- [Python 作用域和命名空间](https://docs.python.org/zh-cn/3/tutorial/classes.html#python-scopes-and-namespaces)
- [执行模型：名称的绑定与解析](https://docs.python.org/zh-cn/3/reference/executionmodel.html#resolution-of-names)
- [Lambda 表达式](https://docs.python.org/zh-cn/3/tutorial/controlflow.html#lambda-expressions)
- [排序指南](https://docs.python.org/zh-cn/3/howto/sorting.html)
- [编程常见问题：为什么 UnboundLocalError](https://docs.python.org/zh-cn/3/faq/programming.html#why-am-i-getting-an-unboundlocalerror-when-the-variable-has-a-value)
