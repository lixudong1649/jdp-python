---
title: 13.4 match 语句
---

# 13.4 match 语句

> 前置：3.1 条件与循环、5.x 类型与结构 · 约 30 分钟 · 官方对应：[match 语句](https://docs.python.org/zh-cn/3/reference/compound_stmts.html#the-match-statement) · 核对日期 2026-10-18（`match` 自 Python 3.10 起可用，课程环境 3.12+）

## 目标

- 用 `match subject:` / `case pattern:` 做结构化分支，替代深层 `if/elif`。
- 会写字面量、序列、映射（字典）模式与 `as` 绑定、`|` 或模式。
- 理解**从上到下**匹配、首个成功分支执行后结束。
- 知道何时用 `match` 更清晰，何时简单 `if` 更合适。

## 核心概念

### 基本形态与通配

`case _:` 是通配分支，通常放在最后：

```python run
def http_label(status: int) -> str:
    match status:
        case 200:
            return "OK"
        case 404:
            return "Not Found"
        case 500 | 502 | 503:
            return "Server Error"
        case _:
            return "Other"

print(http_label(200), http_label(503), http_label(418))
```

### 映射模式（dict）

键名写在 `case` 里，可嵌套绑定变量（适合 JSON / API 消息块）：

```python run
def kind(block: object) -> str:
    match block:
        case {"type": "text", "text": t}:
            return f"text:{t}"
        case {"type": "image", "url": url}:
            return f"image:{url}"
        case {"type": name}:
            return f"other:{name}"
        case _:
            return "unknown"

print(kind({"type": "text", "text": "hi"}))
print(kind({"type": "tool_use", "id": "1"}))
```

### 序列与 as 绑定

列表、元组长度与结构可以一并匹配：

```python run
def describe(point: object) -> str:
    match point:
        case []:
            return "empty"
        case [x]:
            return f"one:{x}"
        case [x, y]:
            return f"pair:{x},{y}"
        case [first, *rest]:
            return f"head:{first}, len_rest:{len(rest)}"
        case _:
            return "not a list"

print(describe([1, 2, 3]), describe((1, 2)))
```

注意 `(1, 2)` 不是 list，会落到 `_`；元组需用 `case (x, y):` 等形式。

### 守卫（guard）

`case` 后可加 `if` 条件，模式绑定成功且条件为真才命中：

```python run
def grade(score: int) -> str:
    match score:
        case s if s < 0:
            return "invalid"
        case s if s >= 90:
            return "A"
        case s if s >= 60:
            return "pass"
        case _:
            return "fail"

print(grade(95), grade(55), grade(-1))
```

### 类模式（了解）

若类定义了 `__match_args__`，可按位置解构（读第三方 SDK 时偶尔见到）：

```python run
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

def quadrant(p: Point) -> str:
    match p:
        case Point(0, 0):
            return "origin"
        case Point(x, y) if x > 0 and y > 0:
            return "Q1"
        case Point(x, y):
            return f"else ({x},{y})"

print(quadrant(Point(1, 2)), quadrant(Point(0, 0)))
```

`dataclass` 会自动生成 `__match_args__`（核对日期 2026-10-18，3.10+ 与 3.12 行为一致）。


## 易错点

- **分支顺序**：更具体的 `case` 要写在更宽泛的上面；`case {"type": name}` 若放在带 `"text"` 键的模式之前，可能抢先匹配。
- **不是 switch 的 fall-through**：命中一个 `case` 后不会继续执行下一个（无 C 语言 `case` 穿透）。
- **误用 match 处理简单标量**：两三个 `if` 更清晰时不要强行 `match`。
- **可变对象与身份**：`match` 比较的是结构/值模式，不是 `is`；单例 `None` 用 `case None:`。
- **忘记通配或后续逻辑**：无一命中时 `match` **不抛异常**，执行落到 `match` 之后；函数若未再 `return`，会得到隐式 `None`。

```python run
def only_one(x):
    match x:
        case 1:
            return "one"

print(only_one(1), only_one(2))
```

## 对照

| 概念 | Python | TS/JS | Java |
|---|---|---|---|
| 结构化分支 | `match` / `case`（3.10+） | 无内置（TS 无完全等价） | `switch`（21+ 增强） |
| 解构 | 序列/映射/类模式 | 解构赋值 | `switch` 模式匹配（21+） |
| 默认分支 | `case _:` | `default` | `default` |
| 守卫 | `case x if cond:` | `if` 链 | `when`（21+） |

## 读代码

读 Agent / Chat API 的**内容块列表**时，常见每个元素是带 `type` 字段的 dict。用 `match` 比长链 `if block["type"] == ...` 更一眼看出支持哪些形态：

```python run
def summarize_block(block: object) -> str:
    match block:
        case {"type": "text", "text": text}:
            return text[:40]
        case {"type": "tool_use", "name": name, "input": inp}:
            return f"tool {name}({list(inp)[:2]})"
        case {"type": t}:
            return f"<{t}>"
        case _:
            return "?"

blocks = [
    {"type": "text", "text": "你好"},
    {"type": "tool_use", "name": "get_weather", "input": {"city": "上海"}},
]
print([summarize_block(b) for b in blocks])
```

阶段 13 项目 `timing.py` 里没有 `match`，但装饰器栈与 `match` 一样讲究**顺序**：多个 `@deco` 从下往上应用；多个 `case` 从上往下匹配。读大型 `match` 时先在纸上列出“谁更具体、谁该在前”。

与 `if/elif` 等价时优先选可读性：模式多于三种、且数据是嵌套结构时，`match` 往往更省脑力。

## 练习

### 练习 1：整数标签

`label(x)`：`1` → `'one'`，其余 → `'other'`。

```python exercise id=s13-l04-match
# --- starter ---
def label(x):
    return 'x'
# --- solution ---
def label(x):
    match x:
        case 1:
            return 'one'
        case _:
            return 'other'
# --- check ---
assert label(1) == 'one' and label(2) == 'other'
```

### 练习 2：事件名解析

`event_name(evt)`：`evt` 为 dict。若有键 `"event"` 且值为字符串则返回该值；否则返回 `"unknown"`。

```python exercise id=s13-l04-event
# --- starter ---
def event_name(evt):
    return "unknown"
# --- solution ---
def event_name(evt):
    match evt:
        case {"event": str(name)}:
            return name
        case _:
            return "unknown"
# --- check ---
assert event_name({"event": "click"}) == "click"
assert event_name({"event": 1}) == "unknown"
assert event_name({}) == "unknown"
```

## 小结

- `match` 对嵌套 dict / 序列做**一次性解构**，`case _` 兜底。
- 分支顺序敏感；无匹配时继续执行 match 之后的代码（易漏 `return`）。
- 守卫 `case x if ...` 在模式成功后进一步筛选。
- Python 3.10 起可用（核对日期 2026-10-18，课程使用 3.12）。

## 延伸阅读

- [match 语句](https://docs.python.org/zh-cn/3/reference/compound_stmts.html#the-match-statement)
- [PEP 634 – Structural Pattern Matching](https://peps.python.org/pep-0634/)
- [PEP 635 – Matching Protocol](https://peps.python.org/pep-0635/)
