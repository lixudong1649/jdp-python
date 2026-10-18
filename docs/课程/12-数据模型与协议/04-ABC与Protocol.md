---
title: 12.4 ABC 与 Protocol
---

# 12.4 ABC 与 Protocol

> 前置：9.2 typing 进阶 · 约 35 分钟 · 官方对应：[abc 模块](https://docs.python.org/zh-cn/3/library/abc.html)、[typing.Protocol](https://docs.python.org/zh-cn/3/library/typing.html#typing.Protocol)

## 目标

- 用 `abc.ABC` 与 `@abstractmethod` **强制**子类实现接口，在实例化时失败。
- 用 `typing.Protocol` 描述**结构化子类型**：不必继承，只要有同名方法即可通过静态检查。
- 理解 Protocol 在运行时基本是“普通类”，类型检查由 mypy / pyright 等完成（核对日期 2026-10-18：项目 Python 3.12；`typing.Protocol` 自 3.8 起稳定，3.15 仍推荐用于鸭子类型标注）。
- 会选择场景：框架扩展点用 ABC，函数参数“只要有某能力”用 Protocol。

## 核心概念

### ABC：名义子类型 + 运行时检查

抽象基类在**定义时**注册到 `abc` 注册表；子类若未实现抽象方法，`classmethod` 检查会在实例化时抛 `TypeError`。

```python run
from abc import ABC, abstractmethod

class Serializer(ABC):
    @abstractmethod
    def dumps(self, obj: object) -> str:
        raise NotImplementedError

class JsonSerializer(Serializer):
    def dumps(self, obj: object) -> str:
        return repr(obj)

print(JsonSerializer().dumps({"a": 1}))
```

若删掉 `dumps` 实现， `JsonSerializer()` 会在 `__init__` 前由 ABC 元类拦截。

### `Protocol`：按能力标注参数

`Protocol` 描述“只要有这些方法就行”，不要求继承关系；静态类型检查器据此验证调用方。

```python run
from typing import Protocol

class SupportsClose(Protocol):
    def close(self) -> None: ...

def shutdown(resource: SupportsClose) -> None:
    resource.close()

class FileLike:
    def close(self) -> None:
        print("closed")

shutdown(FileLike())
```

运行时不强制 `FileLike` 继承 `SupportsClose`；若缺少 `close`，类型检查器报错，但 Python 解释器仍会尝试调用并在运行时 `AttributeError`。

### `runtime_checkable` 与 `isinstance`

部分 Protocol 可加 `@runtime_checkable`，让 `isinstance(x, MyProto)` 在运行时做**粗粒度**结构检查（只验证方法存在，不验证签名）。

```python run
from typing import Protocol, runtime_checkable

@runtime_checkable
class HasLen(Protocol):
    def __len__(self) -> int: ...

print(isinstance([1, 2], HasLen))
print(isinstance("hi", HasLen))
```

未装饰的 Protocol 上 `isinstance` 可能始终为 False；不要依赖 Protocol 做生产环境的权限或安全判断。

### ABC 与 Protocol 如何配合真实代码

库作者常把**对外扩展点**做成 ABC（插件必须子类化），而把**内部函数参数**标成 Protocol（接受任意满足能力的对象）。阶段 12 的 `RingBuffer` 没有继承 ABC，但实现了 `__len__`、`__iter__`，因此满足许多 `Protocol` 形状。

```python run
from collections.abc import Iterable
from typing import Protocol

class SizedIterable(Protocol):
    def __len__(self) -> int: ...
    def __iter__(self): ...

def snapshot(items: SizedIterable) -> list[object]:
    return [x for x in items]

class Pair:
    def __init__(self, a, b):
        self.a, self.b = a, b

    def __len__(self):
        return 2

    def __iter__(self):
        yield self.a
        yield self.b

print(snapshot(Pair(1, 2)))
```


## 易错点

- **忘记实现抽象方法**：实例化子类时 `TypeError: Can't instantiate abstract class ...`。
- **把 Protocol 当运行时护栏**：未加 `runtime_checkable` 时 `isinstance` 不可靠；业务校验应显式调用所需方法或写单元测试。
- **ABC 与多重继承顺序**：抽象方法解析遵循 MRO；混入多个 ABC 时注意元类冲突（少见但难调试）。
- **Protocol 方法体写 `...` 或 `pass`**：只是占位，表示“调用方存在此方法”；不要在里面写业务逻辑。

```python run raises=TypeError
from abc import ABC, abstractmethod

class Repo(ABC):
    @abstractmethod
    def get(self, key: str) -> str: ...

class BrokenRepo(Repo):
    pass

BrokenRepo()
```

## 对照

| 概念 | Python | TS | Java |
|---|---|---|---|
| 显式接口继承 | `class C(ABC)` | `class C implements I` | `class C implements I` |
| 结构类型 | `Protocol` | `interface` 结构兼容 | 无（需显式 implements） |
| 运行时强制 | ABC 实例化检查 | 擦除，主要靠编译器 | `abstract` 类 / 接口 |
| 鸭子类型 | 默认 + Protocol 标注 | 常见 | 需适配器 |

## 读代码

`minimal_agent.py` 用普通 `dict` 把工具名映射到函数，没有用 ABC，但形状上相当于“实现 `__call__` 的可调用对象注册表”：

```python fragment
def get_weather(city):
    """工具的真实实现：这里用固定结果代替真实天气接口。"""
    return f"{city}：晴，22°C"


# 工具名 → 本地函数，用于按模型给出的名字找到要执行的函数
TOOL_FUNCTIONS = {"get_weather": get_weather}
```

- 第 1–3 行：`get_weather` 是具名函数，符合“接收参数并返回 str”的能力，无需继承某个 Tool 基类。
- 第 6 行：注释说明字典用途——按名字分发，是典型的鸭子类型 + 注册表模式。
- 第 7 行：`TOOL_FUNCTIONS` 键是 str，值是 callable；若用 Protocol 可写成 `def run_tool(fn: Callable[..., str], **kw): ...`。
- 模型侧 `tools` 列表用 JSON Schema 描述参数，与 Python 类型是两套系统，通过 `block.name` 和 `block.input` 桥接。
- 若框架要求插件继承 `ToolABC` 并实现 `run`，那就是 ABC 路线；本示例选择最小 dict，便于教学。
- 读大型 SDK 时看到 `class Client(ABC)` 或 `Protocol` 混用：Client 往往 ABC，回调参数往往 Protocol。
- `anthropic` 类型桩文件里大量 `Protocol` 描述响应块；运行时是普通对象属性访问。
- 静态检查通过不等于运行时安全：仍要在循环里判断 `block.type == "tool_use"`。
- 扩展新工具时复制 `get_weather` 模式并更新 `TOOL_FUNCTIONS` 与 `tools` 列表，三处保持一致。
- 用 `typing.TypedDict` 可描述 `messages` 元素形状，与 Protocol 互补。
- 单元测试可对 `TOOL_FUNCTIONS` 的 value 做 `callable` 断言，而不必 `isinstance(..., ToolProtocol)`。

`RingBuffer` 若要与 `collections.abc` 对齐，可显式继承 `Sized` / `Iterable`（ABC 家族），但当前文件选择只实现 dunder，同样能被 `len` 与 `for` 使用——这就是鸭子类型。

## 练习

### 练习 1：Protocol 参数

```python exercise id=s12-l04-proto
# --- starter ---
from typing import Protocol

class Runner(Protocol):
    def run(self) -> str: ...
# --- solution ---
from typing import Protocol

class Runner(Protocol):
    def run(self) -> str: ...

class Job:
    def run(self) -> str:
        return "ok"

def go(r: Runner) -> str:
    return r.run()
# --- check ---
assert go(Job()) == "ok"
```

### 练习 2：抽象基类

实现抽象类 `Greeter`，子类 `HelloGreeter` 的 `greet(name)` 返回 `"Hello, {name}"`。

```python exercise id=s12-l04-abc
# --- starter ---
from abc import ABC, abstractmethod

class Greeter(ABC):
    @abstractmethod
    def greet(self, name: str) -> str:
        raise NotImplementedError
# --- solution ---
from abc import ABC, abstractmethod

class Greeter(ABC):
    @abstractmethod
    def greet(self, name: str) -> str:
        raise NotImplementedError

class HelloGreeter(Greeter):
    def greet(self, name: str) -> str:
        return f"Hello, {name}"
# --- check ---
g = HelloGreeter()
assert g.greet("Ada") == "Hello, Ada"
try:
    Greeter()
    raise AssertionError("不应能实例化 ABC")
except TypeError:
    pass
```


## 小结

- ABC 在实例化时强制实现抽象方法，适合插件与框架基类。
- Protocol 描述能力，静态检查友好，运行时默认不拦鸭子类型。
- `runtime_checkable` 让 `isinstance` 可做粗粒度结构判断，不能替代真正接口契约。
- 读 Agent 注册表：dict + callable 是鸭子类型；类型标注可用 Protocol / `Callable` 表达。

## 延伸阅读

- [abc — 抽象基类](https://docs.python.org/zh-cn/3/library/abc.html)
- [typing.Protocol](https://docs.python.org/zh-cn/3/library/typing.html#typing.Protocol)
- [PEP 544 — Protocols: Structural subtyping](https://peps.python.org/pep-0544/)
