---
title: 9.2 typing 进阶
---

# 9.2 typing 进阶

> 前置：9.1 · 约 35 分钟 · 官方对应：[typing](https://docs.python.org/zh-cn/3/library/typing.html)、[类型相关 PEP 索引](https://peps.python.org/topic/typing/) · 核对日期 2026-10-06

## 目标

- 读懂 SDK 中最常见的高级注解：`Literal`、`TypedDict`、`Callable`、`Iterable`、`Protocol`。
- 读懂泛型：`TypeVar` 旧写法与 3.12 起的 `def f[T](...)`、`type` 别名语句。
- 认识 `@overload`、`TYPE_CHECKING`、`Annotated`、`Self`、`@override`。

## 核心概念

### Literal：取值限定

```python run
from typing import Literal, get_args

StopReason = Literal["end_turn", "max_tokens", "stop_sequence", "tool_use"]
Role = Literal["user", "assistant"]

def is_final(reason: StopReason) -> bool:
    return reason != "tool_use"

print(is_final("end_turn"), get_args(StopReason))
```

`anthropic` 中 `StopReason` 正是这样定义的 `Literal` 别名；类型检查器会拒绝 `is_final("finish")`，运行时则不检查。

### TypedDict：描述 dict 的结构

请求参数常是普通 dict，用 `TypedDict` 描述“有哪些键、每个键什么类型”：

```python run
from typing import Literal, NotRequired, TypedDict

class MessageParam(TypedDict):
    role: Literal["user", "assistant"]
    content: str | list[dict]

class ToolParam(TypedDict):
    name: str
    input_schema: dict
    description: NotRequired[str]     # 可省略的键（3.11 起）

msg: MessageParam = {"role": "user", "content": "你好"}    # 运行时就是普通 dict
tool: ToolParam = {"name": "get_weather", "input_schema": {"type": "object"}}
print(type(msg), msg["role"], MessageParam.__required_keys__)
```

SDK 中名字以 `Param` 结尾的类型（`MessageParam`、`ToolParam`、`TextBlockParam`）多是 `TypedDict`：**你传入普通 dict 即可**，这就是 `minimal_agent.py` 能直接用 dict 字面量构造 `messages` 和 `tools` 的原因。

### Callable 与 collections.abc

```python run
from collections.abc import Callable, Iterable, Iterator, Mapping

ToolFunc = Callable[..., str]            # 任意参数、返回 str 的可调用对象
Handler = Callable[[str, int], bool]     # 接收 (str, int)、返回 bool

def run_all(funcs: Mapping[str, ToolFunc], args: Iterable[dict]) -> Iterator[str]:
    for (name, f), a in zip(funcs.items(), args):
        yield f"{name}: {f(**a)}"

print(list(run_all({"echo": lambda text: text}, [{"text": "hi"}])))
```

参数类型尽量宽（`Iterable`、`Mapping`），返回类型尽量具体（`list`、`dict`）——SDK 签名中大量 `Iterable[...]` 就是这个原因。

### Protocol：结构化类型（鸭子类型）

`Protocol` 只描述“需要有哪些方法/属性”，不要求继承：

```python run
from typing import Protocol, runtime_checkable

@runtime_checkable
class HasText(Protocol):
    text: str

class TextBlock:
    def __init__(self, text: str):
        self.text = text

class ToolUseBlock:
    def __init__(self, name: str):
        self.name = name

def show(block: HasText) -> str:
    return block.text

print(show(TextBlock("你好")))
print(isinstance(TextBlock("x"), HasText), isinstance(ToolUseBlock("x"), HasText))
```

类似 TypeScript 的接口：只要“形状”匹配即可。

### 泛型

```python run
# 3.12 起的类型参数语法（PEP 695）
def first[T](items: list[T]) -> T | None:
    return items[0] if items else None

type Pair[K, V] = tuple[K, V]           # type 别名语句（3.12 起）

class Box[T]:
    def __init__(self, item: T):
        self.item = item

print(first([3, 2, 1]), first(["a"]), Box("x").item, Pair)
```

旧写法（SDK 与老代码中常见，含义相同）：

```python
from typing import Generic, TypeVar

T = TypeVar("T")

def first(items: list[T]) -> T | None: ...

class Box(Generic[T]):
    def __init__(self, item: T) -> None:
        self.item = item
```

### 读 SDK 时常见的其他写法

| 写法 | 含义 |
|---|---|
| `@overload` | 同一函数的多个签名（如 `stream=True` 返回流对象、否则返回 `Message`），只供类型检查，最后一个无装饰器的才是实现 |
| `if TYPE_CHECKING:` | 只在类型检查时导入，运行时不执行（避免循环导入/降低启动开销） |
| `Annotated[T, 元数据]` | 类型 `T` 附带额外信息（如校验规则、判别字段），运行时库可读取 |
| `Self` | 返回“当前类的实例”（3.11 起），常见于链式调用 |
| `@override` | 标记“重写父类方法”（3.12 起，`typing.override`） |
| `TypeAlias` | 显式类型别名（3.10 起；3.12 起推荐 `type X = ...`） |
| `typing_extensions` | 第三方包：把新版 `typing` 特性移植到旧版本，SDK 普遍依赖 |

```python run
from typing import overload

@overload
def parse(value: str) -> int: ...
@overload
def parse(value: bytes) -> str: ...
def parse(value):                       # 真正的实现
    return int(value) if isinstance(value, str) else value.decode()

print(parse("42") + 1, parse(b"hi"))
```

## 易错点

- **`TypedDict` 不是类实例**：`msg.role` 报 `AttributeError`，要用 `msg["role"]`；运行时也不校验键。
- **`@overload` 的签名不执行**：函数体都是 `...`，读码时跳到最后一个定义找实现。
- **在 3.11 及以下使用 `def f[T]` / `type X = ...`**：语法错误；本项目固定 3.12 可用。
- **`Protocol` 默认不支持 `isinstance`**：需要 `@runtime_checkable`，且只检查属性/方法是否存在，不检查类型。

```python run raises=AttributeError
from typing import TypedDict

class MessageParam(TypedDict):
    role: str
    content: str

msg: MessageParam = {"role": "user", "content": "hi"}
print(msg.role)
```

## 对照

| 概念 | Python | TypeScript | Java |
|---|---|---|---|
| 字面量类型 | `Literal["a", "b"]` | `"a" \| "b"` | `enum` |
| 对象形状 | `TypedDict` | `interface` / `type` | `record` / 类 |
| 结构化接口 | `Protocol` | `interface`（结构化） | `interface`（名义，需 implements） |
| 函数类型 | `Callable[[int], str]` | `(x: number) => string` | `Function<Integer, String>` |
| 泛型函数 | `def f[T](x: T) -> T` | `function f<T>(x: T): T` | `<T> T f(T x)` |
| 重载 | `@overload` | 重载签名 | 方法重载 |

## 读代码

`anthropic` 1.11.0 中真实的定义（节选，核对日期 2026-10-06）：

```python
# anthropic/types/stop_reason.py
StopReason: TypeAlias = Literal[
    "end_turn", "max_tokens", "stop_sequence", "tool_use", "pause_turn", "refusal", "model_context_window_exceeded"
]

# anthropic/types/content_block.py
ContentBlock: TypeAlias = Annotated[
    Union[TextBlock, ThinkingBlock, RedactedThinkingBlock, ToolUseBlock, ServerToolUseBlock, ...],
    UnionDiscriminator("type"),
]
```

- `StopReason` 列出了 `resp.stop_reason` 所有可能的值；`minimal_agent.py` 只区分“是不是 `tool_use`”。
- `ContentBlock` 是多种块类型的联合，`Annotated` 附带的 `UnionDiscriminator("type")` 告诉 SDK：**根据 JSON 中的 `type` 字段决定构造哪个类**。这正是我们能用 `b.type == "text"` 判断块类型的根据。
- `Messages.create` 有多个 `@overload`：`stream=False`（默认）返回 `Message`，`stream=True` 返回流对象。

## 练习

### 练习 1：Literal 与运行时校验

定义 `Role = Literal["user", "assistant"]`；实现 `validate_role(value)`：用 `typing.get_args(Role)` 判断，合法则返回该值，否则抛 `ValueError`。

```python exercise id=s09-l02-literal
# --- starter ---
from typing import Literal, get_args

Role = Literal["user"]

def validate_role(value):
    return value
# --- solution ---
from typing import Literal, get_args

Role = Literal["user", "assistant"]

def validate_role(value):
    if value not in get_args(Role):
        raise ValueError(f"非法角色：{value}")
    return value
# --- check ---
assert set(get_args(Role)) == {"user", "assistant"}
assert validate_role("assistant") == "assistant"
try:
    validate_role("system")
except ValueError:
    pass
else:
    raise AssertionError("system 不是合法角色，应抛 ValueError")
```

### 练习 2：泛型函数

用 3.12 的类型参数语法实现 `last[T](items: list[T]) -> T | None`：返回最后一个元素，空列表返回 `None`。

```python exercise id=s09-l02-generic
# --- starter ---
def last(items):
    return items[0]
# --- solution ---
def last[T](items: list[T]) -> T | None:
    return items[-1] if items else None
# --- check ---
assert last([1, 2, 3]) == 3
assert last(["a"]) == "a"
assert last([]) is None
assert len(last.__type_params__) == 1, "请使用 def last[T](...) 语法声明类型参数"
```

### 练习 3：TypedDict

定义 `ToolResultParam(TypedDict)`，键为 `type: Literal["tool_result"]`、`tool_use_id: str`、`content: str`；实现 `make_result(tool_use_id: str, content: str) -> ToolResultParam`。

```python exercise id=s09-l02-typeddict
# --- starter ---
from typing import Literal, TypedDict

def make_result(tool_use_id, content):
    return {}
# --- solution ---
from typing import Literal, TypedDict

class ToolResultParam(TypedDict):
    type: Literal["tool_result"]
    tool_use_id: str
    content: str

def make_result(tool_use_id: str, content: str) -> ToolResultParam:
    return {"type": "tool_result", "tool_use_id": tool_use_id, "content": content}
# --- check ---
assert ToolResultParam.__required_keys__ == frozenset({"type", "tool_use_id", "content"})
r = make_result("t1", "上海：晴")
assert r == {"type": "tool_result", "tool_use_id": "t1", "content": "上海：晴"}
assert type(r) is dict, "TypedDict 实例在运行时就是普通 dict"
```

## 小结

- `Literal` 限定取值，`TypedDict` 描述 dict 结构（SDK 的 `*Param`），`Protocol` 描述“形状”。
- 泛型：3.12 起 `def f[T]`、`class C[T]`、`type X = ...`；旧写法 `TypeVar` + `Generic`。
- `@overload` 只是签名，`TYPE_CHECKING` 块运行时不执行，`Annotated` 携带元数据。

## 延伸阅读

- [typing 模块](https://docs.python.org/zh-cn/3/library/typing.html)
- [PEP 586：Literal](https://peps.python.org/pep-0586/)、[PEP 589：TypedDict](https://peps.python.org/pep-0589/)、[PEP 544：Protocol](https://peps.python.org/pep-0544/)
- [PEP 695：类型参数语法](https://peps.python.org/pep-0695/)
- [collections.abc](https://docs.python.org/zh-cn/3/library/collections.abc.html)
