---
title: 7.3 dataclass 与枚举
---

# 7.3 dataclass 与枚举

> 前置：7.2 · 约 30 分钟 · 官方对应：[dataclasses](https://docs.python.org/zh-cn/3/library/dataclasses.html)、[enum](https://docs.python.org/zh-cn/3/library/enum.html) · 核对日期 2026-10-06

## 目标

- 用 `@dataclass` 定义数据类，知道它自动生成了哪些方法。
- 掌握 `field(default_factory=...)`、`frozen=True`、`asdict`。
- 读懂 `Enum` / `StrEnum`。
- 理解 SDK 响应模型（如 Pydantic 模型）与 dataclass 的相似之处。

## 核心概念

### @dataclass

只需声明字段（带类型注解），`@dataclass` 自动生成 `__init__`、`__repr__`、`__eq__`：

```python run
from dataclasses import dataclass, field, asdict

@dataclass
class ToolUse:
    id: str
    name: str
    input: dict = field(default_factory=dict)   # 可变默认值必须用 default_factory
    type: str = "tool_use"                      # 普通默认值

call = ToolUse("toolu_01", "get_weather", {"city": "上海"})
print(call)                                     # 自动生成的 __repr__
print(call.name, call.input["city"])
print(call == ToolUse("toolu_01", "get_weather", {"city": "上海"}))   # 按字段比较
print(asdict(call))                             # 转为 dict（递归）
```

等价的手写版本要写十几行 `__init__`、`__repr__`、`__eq__`——dataclass 就是为“主要用来装数据的类”减少样板代码。

### 常用参数

| 写法 | 效果 |
|---|---|
| `@dataclass(frozen=True)` | 实例不可修改，并可哈希 |
| `@dataclass(order=True)` | 生成 `<`、`>` 等比较方法 |
| `@dataclass(slots=True)` | 使用 `__slots__`，更省内存（3.10 起） |
| `@dataclass(kw_only=True)` | 所有字段只能用关键字传入（3.10 起） |
| `field(default_factory=list)` | 每个实例一个新列表 |
| `__post_init__` 方法 | 生成的 `__init__` 结束后调用，用于校验或派生字段 |

```python run raises=FrozenInstanceError
from dataclasses import dataclass

@dataclass(frozen=True)
class ProviderConfig:
    base_url: str | None
    key_env: str
    model: str

cfg = ProviderConfig(None, "ANTHROPIC_API_KEY", "claude-haiku-4-5")
print(cfg, hash(cfg) == hash(ProviderConfig(None, "ANTHROPIC_API_KEY", "claude-haiku-4-5")))
cfg.model = "other"      # frozen：不可修改
```

```python run
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class ProviderConfig:
    key_env: str
    model: str

    def __post_init__(self):
        if not self.key_env.endswith("_API_KEY"):
            raise ValueError("key_env 应以 _API_KEY 结尾")

base = ProviderConfig("DEEPSEEK_API_KEY", "deepseek-flash")
custom = replace(base, model="deepseek-pro")   # 基于旧实例创建修改后的新实例
print(base.model, custom.model)
```

注意：dataclass 的类型注解**不做运行时检查**，`ToolUse(1, 2)` 也能创建成功（见 9.1）。

### 枚举 Enum

一组有名字的常量。`StrEnum`（3.11 起）的成员本身就是字符串，适合表示协议中的取值：

```python run
from enum import Enum, StrEnum

class StopReason(StrEnum):
    END_TURN = "end_turn"
    TOOL_USE = "tool_use"
    MAX_TOKENS = "max_tokens"

class Color(Enum):
    RED = 1
    GREEN = 2

r = StopReason("tool_use")          # 由值得到成员
print(r, r is StopReason.TOOL_USE, r == "tool_use")   # StrEnum 可直接与字符串比较
print([s.value for s in StopReason])
print(Color.RED.name, Color.RED.value, Color(2))
```

## 易错点

- **dataclass 字段用可变默认值** `items: list = []`：直接报 `ValueError: mutable default … is not allowed`，用 `field(default_factory=list)`。
- **有默认值的字段后面跟无默认值的字段**：`TypeError: non-default argument … follows default argument`。
- **普通 `Enum` 与字符串比较**：`Color.RED == 1` 为 `False`；需要与原始值比较时用 `.value` 或 `StrEnum`/`IntEnum`。
- **以为注解会校验类型**：不会；需要校验用 `__post_init__` 或 Pydantic 等库。

```python run raises=ValueError
from dataclasses import dataclass

@dataclass
class Conversation:
    messages: list = []
```

## 对照

| 概念 | Python | JS/TS | Java |
|---|---|---|---|
| 数据类 | `@dataclass` | TS `interface` + 对象字面量（仅类型） | `record` |
| 不可变 | `frozen=True` | `Readonly<T>` / `Object.freeze` | `record` 默认不可变 |
| 复制并修改 | `dataclasses.replace(obj, x=1)` | `{...obj, x: 1}` | `withX(...)`（手写） |
| 枚举 | `Enum` / `StrEnum` | TS `enum` / 联合字面量类型 | `enum` |

## 读代码

`anthropic` SDK 的响应对象基于 Pydantic 模型（与 dataclass 思路相同：声明字段 + 自动生成方法，另外会做数据校验与 JSON 转换）。`client.messages.create(...)` 返回的 `Message` 对象大致有这些字段（示意）：

```python
class Message(BaseModel):
    id: str
    type: Literal["message"]
    role: Literal["assistant"]
    model: str
    content: list[ContentBlock]          # TextBlock | ToolUseBlock | ThinkingBlock | ...
    stop_reason: StopReason | None       # "end_turn" | "tool_use" | "max_tokens" | ...
    usage: Usage
```

因此 `resp.stop_reason != "tool_use"` 比较的是一个字符串字段；`resp.content` 是内容块对象的列表。Pydantic 模型提供 `resp.model_dump()`（转 dict）和 `resp.model_dump_json()`（转 JSON），调试时很有用。

## 练习

### 练习 1：定义数据类

用 `@dataclass` 定义 `ToolResult`：字段 `tool_use_id: str`、`content: str`、`type: str = "tool_result"`；并添加方法 `to_dict(self)` 返回 `asdict(self)`。

```python exercise id=s07-l03-dataclass
# --- starter ---
from dataclasses import dataclass, asdict

class ToolResult:
    pass
# --- solution ---
from dataclasses import dataclass, asdict

@dataclass
class ToolResult:
    tool_use_id: str
    content: str
    type: str = "tool_result"

    def to_dict(self):
        return asdict(self)
# --- check ---
r = ToolResult("t1", "上海：晴")
assert r.type == "tool_result"
assert r == ToolResult("t1", "上海：晴"), "dataclass 应按字段比较相等"
assert r.to_dict() == {"tool_use_id": "t1", "content": "上海：晴", "type": "tool_result"}
assert "ToolResult(" in repr(r)
```

### 练习 2：StrEnum

定义 `Role(StrEnum)`，包含 `USER = "user"`、`ASSISTANT = "assistant"`。实现 `is_valid_role(value)`：值是 `Role` 的合法取值时返回 `True`。

```python exercise id=s07-l03-enum
# --- starter ---
from enum import StrEnum

class Role(StrEnum):
    USER = "user"

def is_valid_role(value):
    return True
# --- solution ---
from enum import StrEnum

class Role(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"

def is_valid_role(value):
    return value in {r.value for r in Role}
# --- check ---
assert Role.ASSISTANT == "assistant"
assert is_valid_role("user") and is_valid_role("assistant")
assert not is_valid_role("system")
```

## 小结

- `@dataclass` 根据字段注解生成 `__init__`/`__repr__`/`__eq__`；可变默认值用 `default_factory`。
- `frozen=True` 不可变且可哈希，`replace()` 生成修改后的副本。
- `StrEnum` 成员即字符串，适合协议取值；普通 `Enum` 比较要用 `.value`。
- SDK 响应模型（Pydantic）可类比 dataclass：按字段访问属性。

## 延伸阅读

- [dataclasses](https://docs.python.org/zh-cn/3/library/dataclasses.html)
- [enum](https://docs.python.org/zh-cn/3/library/enum.html)、[枚举指南](https://docs.python.org/zh-cn/3/howto/enum.html)
- [PEP 557：数据类](https://peps.python.org/pep-0557/)
