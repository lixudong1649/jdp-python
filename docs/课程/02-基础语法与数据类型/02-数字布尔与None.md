---
title: 2.2 数字、布尔与 None
---

# 2.2 数字、布尔与 None

> 前置：2.1 · 约 25 分钟 · 官方对应：[数字](https://docs.python.org/zh-cn/3/tutorial/introduction.html#numbers)、[内置类型：真值检测](https://docs.python.org/zh-cn/3/library/stdtypes.html#truth-value-testing)

## 目标

- 掌握 `int`、`float` 的运算规则，尤其是 `/`、`//`、`%` 与浮点误差。
- 理解真值（truthiness）以及 `and` / `or` **返回操作数本身**。
- 读懂 `x or 默认值`、`x is None` 等惯用写法。

## 核心概念

### 数字

| 类型 | 特点 |
|---|---|
| `int` | 任意精度整数，不会溢出 |
| `float` | IEEE 754 双精度浮点数，有舍入误差 |
| `complex` | 复数 `1+2j`（读码中少见） |

| 运算 | 含义 | 例子 |
|---|---|---|
| `/` | 真除法，结果总是 `float` | `7 / 2 == 3.5` |
| `//` | 向下取整除法（floor） | `7 // 2 == 3`，`-7 // 2 == -4` |
| `%` | 取模，符号与除数相同 | `-7 % 2 == 1` |
| `**` | 幂 | `2 ** 10 == 1024` |
| `divmod(a, b)` | 同时得到 `(a // b, a % b)` | `divmod(7, 2) == (3, 1)` |

```python run
print(7 / 2, 7 // 2, 7 % 2)
print(-7 // 2, -7 % 2)        # 向下取整：-4，余数 1
print(2 ** 100)               # 大整数不会溢出
print(0.1 + 0.2)              # 0.30000000000000004
print(round(0.1 + 0.2, 2))    # 0.3
print(int("42") + 1, float("3.5"), int(3.9))  # 转换；int() 向零截断
print(1_000_000)              # 数字中的下划线只为可读性
```

比较浮点数用 `math.isclose`；`round()` 采用“银行家舍入”（四舍六入五成双）：

```python run
import math

print(math.isclose(0.1 + 0.2, 0.3))  # True
print(round(2.5), round(3.5))         # 2 4
```

### 布尔与比较

`bool` 只有 `True` 和 `False` 两个值，是 `int` 的子类（`True == 1`）。比较运算可以**链式**书写：

```python run
age = 30
print(18 <= age < 60)        # 等价 18 <= age and age < 60
print(True + True)           # 2：bool 是 int 的子类
print(isinstance(True, int))
```

### 真值检测

在 `if`、`while`、`and`、`or`、`not` 中，任何对象都可以当作条件。以下值为**假**，其余为真：

- `None`、`False`
- 数值零：`0`、`0.0`
- 空容器：`""`、`[]`、`()`、`{}`、`set()`、`range(0)`

```python run
for value in [None, 0, "", [], {}, "0", [0], -1]:
    print(repr(value), "→", bool(value))
```

### `and` / `or` 返回操作数

`and`、`or` 是短路运算，**返回最后被求值的那个操作数**，不一定是布尔值：

| 表达式 | 规则 | 例子 |
|---|---|---|
| `a or b` | `a` 为真返回 `a`，否则返回 `b` | `"" or "默认" == "默认"` |
| `a and b` | `a` 为假返回 `a`，否则返回 `b` | `0 and 1/0` 返回 `0`，不会除零 |
| `not a` | 总是返回 `bool` | `not ""` 的结果是 `True` |

```python run
print(None or "deepseek")       # deepseek
print("anthropic" or "deepseek")  # anthropic
print("" or "deepseek")         # 空字符串为假 → deepseek
print([] and "不会求值")          # []
print(0 or None)                # None：两个都假，返回最后一个
```

### None

`None` 表示“没有值”，是 `NoneType` 的唯一实例。函数没有 `return` 时返回 `None`；字典 `get` 找不到键时返回 `None`。判断用 `is None` / `is not None`。

```python run
def no_return():
    pass

result = no_return()
print(result, result is None)
print({"a": 1}.get("b"))
```

## 易错点

- **`or` 会吞掉合法的假值**：`timeout = user_timeout or 30`，当用户传 `0` 时也会变成 `30`。需要区分“没传”和“传了 0”时，用 `30 if user_timeout is None else user_timeout`。
- **浮点数直接 `==` 比较**：用 `math.isclose`，涉及金额用 `decimal.Decimal`。
- **`int()` 不是四舍五入**：`int(3.9) == 3`（向零截断）。
- **`"1" + 1`**：不同类型不会隐式转换，抛 `TypeError`。

```python run raises=TypeError
print("1" + 1)
```

## 对照

| 行为 | Python | JS | Java |
|---|---|---|---|
| 整数 | `int` 任意精度 | `number`（双精度）/ `bigint` | `int`/`long` 会溢出 |
| `7 / 2` | `3.5` | `3.5` | `3`（整数除法） |
| 整除 | `7 // 2` | `Math.floor(7 / 2)` | `7 / 2` |
| 空值 | `None` | `null` / `undefined` | `null` |
| 默认值 | `a or b`（假值都触发） | `a \|\| b`；`a ?? b`（仅 null/undefined） | `Objects.requireNonNullElse(a, b)` |
| 逻辑运算符 | `and` `or` `not` | `&&` `\|\|` `!` | `&&` `\|\|` `!` |

Python 没有 `??`；需要“只在 None 时取默认值”就写条件表达式。

## 读代码

```python
provider = os.getenv("LLM_PROVIDER") or "deepseek"
model = os.getenv("LLM_MODEL") or config["model"]
```

`os.getenv` 在环境变量不存在时返回 `None`；`.env` 中写了 `LLM_PROVIDER=`（空值）时返回 `""`。两者都为假，所以都会回退到默认值。这正是这里选用 `or` 而不是 `is None` 判断的原因：**空字符串也应视为“未配置”**。

`"base_url": None` 表示“不指定”。anthropic 1.11.0 的 `_client.py` 中：`base_url is None` 时先读环境变量 `ANTHROPIC_BASE_URL`，仍为空才用 `https://api.anthropic.com`（核对日期 2026-10-06）。

## 练习

### 练习 1：配置默认值

实现 `pick_provider(env_value)`：`env_value` 为 `None` 或空字符串时返回 `"deepseek"`，否则返回原值。用 `or` 一行写完。

```python exercise id=s02-l02-or-default
# --- starter ---
def pick_provider(env_value):
    ...
# --- solution ---
def pick_provider(env_value):
    return env_value or "deepseek"
# --- check ---
assert pick_provider(None) == "deepseek"
assert pick_provider("") == "deepseek"
assert pick_provider("anthropic") == "anthropic"
```

### 练习 2：区分“没传”与“传了 0”

实现 `get_timeout(value)`：`value is None` 时返回 `30`，否则原样返回（包括 `0`）。

```python exercise id=s02-l02-none-default
# --- starter ---
def get_timeout(value):
    return value or 30
# --- solution ---
def get_timeout(value):
    return 30 if value is None else value
# --- check ---
assert get_timeout(None) == 30
assert get_timeout(0) == 0, "传入 0 时应返回 0，而不是默认值"
assert get_timeout(5) == 5
```

### 练习 3：分钟换算

实现 `fmt_duration(seconds)`，把非负整数秒数转为 `"X分Y秒"`，例如 `125` → `"2分5秒"`。提示：`divmod`。

```python exercise id=s02-l02-divmod
# --- starter ---
def fmt_duration(seconds):
    ...
# --- solution ---
def fmt_duration(seconds):
    m, s = divmod(seconds, 60)
    return f"{m}分{s}秒"
# --- check ---
assert fmt_duration(125) == "2分5秒", fmt_duration(125)
assert fmt_duration(59) == "0分59秒"
assert fmt_duration(3600) == "60分0秒"
```

## 小结

- `/` 总得 `float`，`//` 向下取整，浮点有误差。
- `None`、`0`、空容器为假；`and`/`or` 返回操作数本身。
- `x or 默认` 适合“空值也算未设置”的场景；只在 `None` 时取默认用条件表达式。

## 延伸阅读

- [Python 速览：数字](https://docs.python.org/zh-cn/3/tutorial/introduction.html#numbers)
- [内置类型：真值检测、布尔运算、数字类型](https://docs.python.org/zh-cn/3/library/stdtypes.html#truth-value-testing)
- [浮点算术：争议和限制](https://docs.python.org/zh-cn/3/tutorial/floatingpoint.html)
- [表达式：布尔运算](https://docs.python.org/zh-cn/3/reference/expressions.html#boolean-operations)
