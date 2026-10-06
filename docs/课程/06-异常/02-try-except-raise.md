---
title: 6.2 try / except / raise
---

# 6.2 try / except / raise

> 前置：6.1 · 约 35 分钟 · 官方对应：[处理异常](https://docs.python.org/zh-cn/3/tutorial/errors.html#handling-exceptions)、[触发异常](https://docs.python.org/zh-cn/3/tutorial/errors.html#raising-exceptions) · 核对日期 2026-10-06

## 目标

- 读懂 `try / except / else / finally` 的执行顺序。
- 用 `raise` 主动抛出异常，用 `raise … from …` 保留异常链。
- 定义自定义异常类，理解异常的继承层次（`except` 父类会捕获子类）。
- 判断什么时候该捕获、什么时候该让它抛出。

## 核心概念

### 基本结构

```python run
def to_int(text):
    try:
        value = int(text)            # 可能出错的代码
    except ValueError as e:          # 只捕获预期的异常类型；e 是异常对象
        print(f"无法转换 {text!r}：{e}")
        return None
    else:                            # try 中没有异常时执行
        print("转换成功")
        return value
    finally:                         # 无论如何都执行（清理资源）
        print("finally 总会执行")

print(to_int("42"))
print(to_int("4x"))
```

### 捕获多种异常

```python run
def risky(kind):
    if kind == "key":
        return {}["x"]
    if kind == "type":
        return "1" + 1
    return 1 / 0

for kind in ["key", "type", "zero"]:
    try:
        risky(kind)
    except (KeyError, TypeError) as e:    # 元组：任一类型
        print("数据问题：", type(e).__name__)
    except ZeroDivisionError:
        print("除零")
```

Python 3.14 起，不使用 `as` 时可以省略括号：`except KeyError, TypeError:`（[PEP 758](https://peps.python.org/pep-0758/)，核对日期 2026-10-06）。为兼容 3.12/3.13，本课程保留括号写法。

### 异常层次

异常是类，按继承组织。`except 父类` 会捕获所有子类：

```text
BaseException
 ├── KeyboardInterrupt、SystemExit   ← 不应被普通代码捕获
 └── Exception                       ← 一般捕获到这里为止
      ├── LookupError
      │    ├── KeyError
      │    └── IndexError
      ├── ValueError
      ├── TypeError
      ├── OSError
      │    └── FileNotFoundError
      └── ……
```

```python run
try:
    [][0]
except LookupError as e:          # IndexError 是 LookupError 的子类
    print("捕获到", type(e).__name__, isinstance(e, LookupError))
print(KeyError.__mro__)           # 继承链
```

### 主动抛出与自定义异常

```python run
class ToolError(Exception):
    """工具执行失败。"""

class UnknownToolError(ToolError):
    def __init__(self, name):
        super().__init__(f"未知工具：{name}")
        self.name = name

def run_tool(name):
    if name != "get_weather":
        raise UnknownToolError(name)
    return "晴"

try:
    run_tool("get_time")
except ToolError as e:            # 用父类捕获整个类别
    print(type(e).__name__, "|", e, "|", e.name)
```

### 异常链：raise … from …

把底层异常转换为更有业务含义的异常时，用 `from` 保留原因，Traceback 中会显示 “The above exception was the direct cause of the following exception”：

```python run raises=ToolError
class ToolError(Exception):
    pass

def run_tool(functions, name, tool_input):
    try:
        return functions[name](**tool_input)
    except KeyError as e:
        raise ToolError(f"未知工具 {name!r}") from e

run_tool({}, "get_time", {})
```

### 什么时候捕获

- **只捕获你能处理的具体异常**，并在 `try` 中只放可能出错的那一两行。
- 处理不了就让它抛出：程序崩溃并给出 Traceback，比静默吞掉错误更容易排查。
- Python 风格偏向 **EAFP**（先做，出错再处理）而不是 LBYL（先检查再做）：

```python run
config = {"model": "m"}
# LBYL
timeout = config["timeout"] if "timeout" in config else 30
# EAFP
try:
    timeout = config["timeout"]
except KeyError:
    timeout = 30
print(timeout)
```

## 易错点

- **裸 `except:` 或 `except Exception: pass`**：吞掉所有错误（裸 `except` 连 `Ctrl-C` 都会吞），问题被隐藏。至少要记录日志或重新抛出。
- **`try` 块过大**：捕获到的异常可能来自意料之外的行。
- **在 `except` 中写 `raise e`** 与单独写 `raise`：后者原样重新抛出，保留原始 Traceback，更推荐。
- **`finally` 中 `return`** 会覆盖异常与 try 中的返回值，应避免（3.14 起会产生 `SyntaxWarning`，[PEP 765](https://peps.python.org/pep-0765/)）。

```python run
def swallow():
    try:
        return 1 / 0
    except Exception:
        pass            # 错误被吞掉，函数返回 None，调用方不知道发生了什么

print(swallow())
```

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 捕获 | `try: … except E as e:` | `try {} catch (e) {}` | `try {} catch (E e) {}` |
| 按类型捕获 | 多个 `except` | 手动 `instanceof` | 多个 `catch` |
| 无异常时 | `else:` | 无 | 无 |
| 清理 | `finally:` | `finally` | `finally` / try-with-resources |
| 抛出 | `raise E("msg")` | `throw new Error("msg")` | `throw new E("msg")` |
| 异常链 | `raise E() from e` | `new Error(msg, { cause: e })` | `new E(msg, e)` |
| 受检异常 | 无 | 无 | 有（checked exception） |

## 读代码

`minimal_agent.py` 没有任何 `try`：任何异常都会直接终止程序并打印 Traceback。对一个演示脚本来说这是合理的选择——错误立即可见。生产代码通常会这样包装 SDK 调用（示意）：

```python
import anthropic

try:
    resp = client.messages.create(model=model, max_tokens=1024, tools=tools, messages=messages)
except anthropic.AuthenticationError:
    raise SystemExit("API 密钥无效：检查 .env 中的 DEEPSEEK_API_KEY")
except anthropic.RateLimitError:
    ...  # 等待后重试
except anthropic.APIError as e:
    raise RuntimeError("模型服务调用失败") from e
```

SDK 定义了一组异常类：先写最具体的（`AuthenticationError`、`RateLimitError`），最后写父类 `APIError` 兜底——顺序反了的话，父类会先把子类全部截走。

## 练习

### 练习 1：安全执行工具

实现 `safe_run(functions, name, tool_input)`：

- 工具名不存在 → 返回 `"错误：未知工具 <name>"`；
- 参数不匹配（调用时抛 `TypeError`）→ 返回 `"错误：参数不匹配"`；
- 正常 → 返回工具结果。

只捕获这两种情况，其他异常照常抛出。

```python exercise id=s06-l02-safe-run
# --- starter ---
def safe_run(functions, name, tool_input):
    return functions[name](**tool_input)
# --- solution ---
def safe_run(functions, name, tool_input):
    func = functions.get(name)
    if func is None:
        return f"错误：未知工具 {name}"
    try:
        return func(**tool_input)
    except TypeError:
        return "错误：参数不匹配"
# --- check ---
def get_weather(city):
    return f"{city}：晴"

def broken(city):
    return 1 / 0

F = {"get_weather": get_weather, "broken": broken}
assert safe_run(F, "get_weather", {"city": "上海"}) == "上海：晴"
assert safe_run(F, "get_time", {}) == "错误：未知工具 get_time"
assert safe_run(F, "get_weather", {"town": "上海"}) == "错误：参数不匹配"
try:
    safe_run(F, "broken", {"city": "x"})
except ZeroDivisionError:
    pass
else:
    raise AssertionError("其他异常（如 ZeroDivisionError）不应被吞掉")
```

### 练习 2：自定义异常与异常链

定义 `ConfigError(Exception)`。实现 `load_provider(providers, name)`：返回 `providers[name]`；键不存在时抛出 `ConfigError(f"未知 provider: {name}")`，并用 `from` 链接原始 `KeyError`。

```python exercise id=s06-l02-chain
# --- starter ---
class ConfigError(Exception):
    pass

def load_provider(providers, name):
    return providers[name]
# --- solution ---
class ConfigError(Exception):
    pass

def load_provider(providers, name):
    try:
        return providers[name]
    except KeyError as e:
        raise ConfigError(f"未知 provider: {name}") from e
# --- check ---
assert load_provider({"deepseek": 1}, "deepseek") == 1
try:
    load_provider({"deepseek": 1}, "foo")
except ConfigError as e:
    assert str(e) == "未知 provider: foo", str(e)
    assert isinstance(e.__cause__, KeyError), "应使用 raise ... from e 保留原始 KeyError"
else:
    raise AssertionError("应抛出 ConfigError")
```

## 小结

- `try/except/else/finally`：`else` 在无异常时执行，`finally` 总执行。
- `except 父类` 捕获所有子类；具体的写前面。
- `raise` 抛出，`raise X from e` 保留原因，单独 `raise` 原样重抛。
- 只捕获能处理的具体异常，不要静默吞掉错误。

## 延伸阅读

- [错误和异常（教程）](https://docs.python.org/zh-cn/3/tutorial/errors.html)
- [异常链](https://docs.python.org/zh-cn/3/tutorial/errors.html#exception-chaining)
- [用户自定义异常](https://docs.python.org/zh-cn/3/tutorial/errors.html#user-defined-exceptions)
- [内置异常层次](https://docs.python.org/zh-cn/3/library/exceptions.html#exception-hierarchy)
- [PEP 758：不带括号的 except](https://peps.python.org/pep-0758/)
