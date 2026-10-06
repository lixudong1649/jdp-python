---
title: 10.4 读第三方 SDK 代码
---

# 10.4 读第三方 SDK 代码

> 前置：10.1–10.3、阶段 7、阶段 9 · 约 40 分钟 · 官方对应：[inspect](https://docs.python.org/zh-cn/3/library/inspect.html)、[functools.cached_property](https://docs.python.org/zh-cn/3/library/functools.html#functools.cached_property)、[uv：管理依赖](https://docs.astral.sh/uv/concepts/projects/dependencies/) · 核对日期 2026-10-06（`anthropic` 1.11.0）

## 目标

- 从一行调用 `client.messages.create(...)` 出发，定位到 SDK 源码中的定义。
- 读懂 SDK 的五个常见模式：资源对象与 `cached_property`、仅限关键字参数 + 哨兵默认值、`@overload`、类型化响应模型、异常层次。
- 用一个结构相同的迷你 SDK 在浏览器中验证理解。

## 核心概念

### 第一步：找到源码

在项目根目录执行（真实 SDK 只能在本地环境中查看）：

```bash
uv run python -c "import anthropic; print(anthropic.__version__, anthropic.__file__)"
uv run python -c "import anthropic, inspect; print(inspect.getsourcefile(anthropic.Anthropic))"
uv run python -c "import anthropic.resources.messages as m, inspect; print(inspect.getsourcefile(m.Messages))"
```

也可以在编辑器中按住 Cmd 点击名字跳转。SDK 安装在 `.venv/lib/python3.12/site-packages/anthropic/`，常用位置：

| 文件 | 内容 |
|---|---|
| `anthropic/__init__.py` | 公开接口：`Anthropic`、各异常类、`types` |
| `anthropic/_client.py` | `class Anthropic`：鉴权、`base_url`、各资源属性 |
| `anthropic/resources/messages/messages.py` | `class Messages`：`create`、`stream`、`count_tokens` |
| `anthropic/types/` | 请求参数（`*Param`，TypedDict）与响应模型（`Message`、`TextBlock`……） |
| `anthropic/_exceptions.py` | 异常层次 |

### 模式 1：资源对象 + cached_property

`anthropic/_client.py` 中（1.11.0，节选）：

```python
class Anthropic(SyncAPIClient):
    ...
    @cached_property
    def messages(self) -> Messages:
        from .resources.messages import Messages

        return Messages(self)
```

- `client.messages` 是一个**属性**（不加括号），首次访问时创建 `Messages(self)` 并缓存；资源对象持有对客户端的引用，以便复用连接和鉴权信息。
- 方法体内的 `import` 是延迟导入，减少 `import anthropic` 的启动开销。

### 模式 2：仅限关键字参数 + 哨兵默认值

```python fragment
@overload
def create(
    self,
    *,
    max_tokens: int,
    messages: Iterable[MessageParam],
    model: ModelParam,
    stream: Literal[False] | Omit = omit,
    tools: Iterable[ToolUnionParam] | Omit = omit,
    ...
) -> Message: ...
```

- `*`：后面全部只能用关键字传（3.3）。
- `= omit`：可选参数的默认值不是 `None`，而是一个特殊的**哨兵对象**，用来区分“没传”和“显式传了 `None`”（`None` 在 API 中可能有含义）。发请求时，值为 `omit` 的参数不会出现在请求体里。
- 多个 `@overload`（9.2）：`stream` 不传或为 `False` 时返回 `Message`，为 `True` 时返回流对象；真正的实现在最后一个无 `@overload` 的 `create` 中。

### 模式 3：类型化响应模型

响应 JSON 被转换为模型对象：`Message` 的 `content` 是 `list[ContentBlock]`，而 `ContentBlock` 是带判别字段 `type` 的联合类型（9.2）。所以你写 `block.type`、`block.name`，而不是 `block["type"]`。

### 模式 4：异常层次

```text
AnthropicError
 └── APIError
      ├── APIConnectionError
      │    └── APITimeoutError
      └── APIStatusError            ← 有 HTTP 状态码
           ├── BadRequestError       (400)
           ├── AuthenticationError   (401)
           ├── PermissionDeniedError (403)
           ├── NotFoundError         (404)
           ├── RateLimitError        (429)
           └── InternalServerError   (>=500)
```

（节选自 1.11.0 的 `anthropic/_exceptions.py`；另有 `ConflictError`(409)、`RequestTooLargeError`(413)、`UnprocessableEntityError`(422)、`ServiceUnavailableError`(503)、`DeadlineExceededError`(504)、`OverloadedError`(529) 等子类。）

### 迷你 SDK：同样的结构，可在浏览器运行

```python run
from dataclasses import dataclass
from functools import cached_property


class _Omit:
    """哨兵：表示“调用方没有传这个参数”。"""
    def __repr__(self):
        return "omit"

omit = _Omit()


class APIError(Exception): ...
class AuthenticationError(APIError): ...


@dataclass
class TextBlock:
    text: str
    type: str = "text"

@dataclass
class ToolUseBlock:
    id: str
    name: str
    input: dict
    type: str = "tool_use"

BLOCK_TYPES = {"text": TextBlock, "tool_use": ToolUseBlock}   # 判别字段 → 模型类

@dataclass
class Message:
    content: list
    stop_reason: str


class Messages:
    def __init__(self, client):
        self._client = client

    def create(self, *, model, max_tokens, messages, tools=omit, temperature=omit):
        body = {"model": model, "max_tokens": max_tokens, "messages": messages,
                "tools": tools, "temperature": temperature}
        body = {k: v for k, v in body.items() if v is not omit}       # 去掉没传的参数
        raw = self._client._post("/v1/messages", body)                 # 返回 JSON（dict）
        blocks = [BLOCK_TYPES[b["type"]](**b) for b in raw["content"]] # dict → 模型对象
        return Message(content=blocks, stop_reason=raw["stop_reason"])


class FakeAnthropic:
    def __init__(self, *, api_key=None, base_url=None):
        if not api_key:
            raise AuthenticationError("缺少 api_key")
        self.api_key = api_key
        self.base_url = base_url or "https://api.anthropic.com"

    @cached_property
    def messages(self):
        print("（首次访问 client.messages，创建资源对象）")
        return Messages(self)

    def _post(self, path, body):
        print(f"POST {self.base_url}{path} 请求体键：{sorted(body)}")
        return {"content": [{"type": "text", "text": "你好！"}], "stop_reason": "end_turn"}


client = FakeAnthropic(api_key="sk-demo", base_url="https://api.deepseek.com/anthropic")
resp = client.messages.create(model="deepseek-flash", max_tokens=64, messages=[{"role": "user", "content": "hi"}])
print(resp)
print(client.messages is client.messages)          # cached_property：同一个对象
print(resp.content[0].type, resp.content[0].text)
try:
    FakeAnthropic()
except APIError as e:                               # 用父类捕获
    print(type(e).__name__, e)
```

## 易错点

- **把 `client.messages` 当方法调用**：`client.messages()` 报 `TypeError: 'Messages' object is not callable`。
- **把响应对象当 dict**：`resp["content"]` 报 `TypeError`（不可下标）；用属性访问，或 `resp.model_dump()` 转 dict。
- **把 `omit`/`NOT_GIVEN` 与 `None` 混为一谈**：显式传 `None` 可能被发送给服务端。
- **直接阅读最底层的 HTTP 代码**：大多数问题在公开方法的签名、文档字符串和类型定义中就能找到答案。

```python run raises=TypeError
class Message:
    def __init__(self):
        self.content = []

resp = Message()
print(resp["content"])
```

## 对照

| 模式 | Python SDK | JS/TS SDK | Java SDK |
|---|---|---|---|
| 资源分组 | `client.messages.create(...)` | `client.messages.create({...})` | `client.messages().create(params)` |
| 参数传递 | 关键字参数 | 单个参数对象 | Builder |
| 可选参数缺省 | 哨兵 `omit` / `NOT_GIVEN` | 属性不存在（`undefined`） | Builder 不设置 |
| 响应 | Pydantic 模型（属性访问） | 普通对象 + TS 类型 | 不可变类 + getter |
| 异常 | 类层次 + `except` | 类层次 + `instanceof` | 类层次 + `catch` |

## 读代码

把 `minimal_agent.py` 中与 SDK 交互的每一处对应到源码：

| `minimal_agent.py` | SDK 中的位置 | 说明 |
|---|---|---|
| `anthropic.Anthropic(api_key=..., base_url=...)` | `_client.py` 的 `class Anthropic.__init__` | `base_url=None` 时先读 `ANTHROPIC_BASE_URL`，再回退官方地址；`api_key=None` 且无其他凭据时回退读取 `ANTHROPIC_API_KEY`（8.3） |
| `client.messages` | `_client.py` 的 `@cached_property def messages` | 资源对象 |
| `.create(model=..., max_tokens=1024, tools=tools, messages=messages)` | `resources/messages/messages.py` 的 `create` | 必填 `max_tokens`、`messages`、`model` |
| `resp.content` / `resp.stop_reason` | `types/message.py` 的 `class Message` | `content: List[ContentBlock]`，`stop_reason: Optional[StopReason]` |
| `b.type == "text"` / `b.text` | `types/text_block.py` | `type: Literal["text"]`、`text: str` |
| `block.id` / `block.name` / `block.input` | `types/tool_use_block.py` | `input: Dict[str, object]` |

`messages` 与 `tools` 用普通 dict 构造即可，因为它们的类型 `MessageParam`、`ToolParam` 是 `TypedDict`（9.2）。而 `messages.append({"role": "assistant", "content": resp.content})` 把**模型对象列表**放回请求中——SDK 序列化请求时同样接受这些对象。

## 练习

### 练习 1：判别字段构造模型

实现 `parse_blocks(raw_blocks)`：按每个 dict 的 `"type"` 从 `BLOCK_TYPES` 中选择类，用其余字段构造对象（`type` 字段也一并传入）；遇到未知类型时跳过。

```python exercise id=s10-l04-parse
# --- starter ---
from dataclasses import dataclass

@dataclass
class TextBlock:
    text: str
    type: str = "text"

@dataclass
class ToolUseBlock:
    id: str
    name: str
    input: dict
    type: str = "tool_use"

BLOCK_TYPES = {"text": TextBlock, "tool_use": ToolUseBlock}

def parse_blocks(raw_blocks):
    return raw_blocks
# --- solution ---
from dataclasses import dataclass

@dataclass
class TextBlock:
    text: str
    type: str = "text"

@dataclass
class ToolUseBlock:
    id: str
    name: str
    input: dict
    type: str = "tool_use"

BLOCK_TYPES = {"text": TextBlock, "tool_use": ToolUseBlock}

def parse_blocks(raw_blocks):
    result = []
    for raw in raw_blocks:
        cls = BLOCK_TYPES.get(raw.get("type"))
        if cls is not None:
            result.append(cls(**raw))
    return result
# --- check ---
raw = [
    {"type": "thinking", "thinking": "..."},
    {"type": "text", "text": "我查一下"},
    {"type": "tool_use", "id": "t1", "name": "get_weather", "input": {"city": "上海"}},
]
blocks = parse_blocks(raw)
assert [type(b).__name__ for b in blocks] == ["TextBlock", "ToolUseBlock"], blocks
assert blocks[1].name == "get_weather" and blocks[1].input == {"city": "上海"}
assert blocks[0].type == "text"
```

### 练习 2：哨兵参数

实现 `build_body(*, model, max_tokens, temperature=omit, system=omit)`：返回只包含**实际传入**参数的 dict。注意：显式传入 `None` 也应保留在结果中。

```python exercise id=s10-l04-omit
# --- starter ---
class _Omit:
    def __repr__(self):
        return "omit"

omit = _Omit()

def build_body(*, model, max_tokens, temperature=None, system=None):
    body = {"model": model, "max_tokens": max_tokens, "temperature": temperature, "system": system}
    return {k: v for k, v in body.items() if v is not None}
# --- solution ---
class _Omit:
    def __repr__(self):
        return "omit"

omit = _Omit()

def build_body(*, model, max_tokens, temperature=omit, system=omit):
    body = {"model": model, "max_tokens": max_tokens, "temperature": temperature, "system": system}
    return {k: v for k, v in body.items() if v is not omit}
# --- check ---
assert build_body(model="m", max_tokens=10) == {"model": "m", "max_tokens": 10}
assert build_body(model="m", max_tokens=10, temperature=0) == {"model": "m", "max_tokens": 10, "temperature": 0}
assert build_body(model="m", max_tokens=10, system=None) == {"model": "m", "max_tokens": 10, "system": None}, "显式传入的 None 应保留"
```

## 小结

- 定位源码：`模块.__file__`、`inspect.getsourcefile`、编辑器跳转；从 `__init__.py` 找到真正定义。
- SDK 五模式：资源对象（`cached_property`）、仅限关键字 + 哨兵、`@overload`、类型化模型（判别字段）、异常层次。
- 读 SDK 先看签名、文档字符串与类型定义，最后才看 HTTP 细节。

## 延伸阅读

- [inspect](https://docs.python.org/zh-cn/3/library/inspect.html)
- [functools.cached_property](https://docs.python.org/zh-cn/3/library/functools.html#functools.cached_property)
- [typing.overload](https://docs.python.org/zh-cn/3/library/typing.html#typing.overload)
- [uv：管理依赖（查看已安装的包）](https://docs.astral.sh/uv/concepts/projects/dependencies/)
