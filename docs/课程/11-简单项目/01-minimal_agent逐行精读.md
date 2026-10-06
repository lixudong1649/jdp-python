---
title: 11.1 minimal_agent.py 逐行精读
---

# 11.1 minimal_agent.py 逐行精读

> 前置：阶段 1–10 · 约 60 分钟 · 源文件：[examples/agent/minimal_agent.py](../../../examples/agent/minimal_agent.py) · 核对日期 2026-10-06（`anthropic` 1.11.0）

## 目标

- 逐段讲清 `minimal_agent.py` 的每一行：做什么、用到哪一课的语法。
- 画出 `messages` 在每一轮之后的结构。
- 在浏览器中用模拟客户端运行**完整的 Agent 循环**，修改并观察结果。

## 核心概念

### 全文

下面是仓库中 `examples/agent/minimal_agent.py` 的完整内容（校验器会确认此副本与源文件逐字一致）：

```python source=examples/agent/minimal_agent.py
"""最小 Agent 循环示例（Anthropic Messages API 工具调用）。

循环：模型决定是否调用工具 → 本地执行工具 → 把结果喂回模型 → 直到给出最终回答或达到最大轮数。
同一份代码可切换模型服务（环境变量 LLM_PROVIDER）：
  - deepseek（默认）：DeepSeek 的 Anthropic 兼容端点，读取 DEEPSEEK_API_KEY
  - anthropic：Anthropic 官方 API，读取 ANTHROPIC_API_KEY

运行（在项目根目录）：uv run examples/agent/minimal_agent.py
"""

import os

import anthropic
from dotenv import load_dotenv

# 从项目根目录的 .env 读取密钥等配置（.env 已被 git 忽略）
load_dotenv()

# 各模型服务的连接参数：base_url 为 None 表示使用 SDK 默认的 Anthropic 官方地址
PROVIDERS = {
    "deepseek": {
        "base_url": "https://api.deepseek.com/anthropic",
        "key_env": "DEEPSEEK_API_KEY",
        "model": "deepseek-flash",
    },
    "anthropic": {
        "base_url": None,
        "key_env": "ANTHROPIC_API_KEY",
        "model": "claude-haiku-4-5",
    },
}
MAX_TURNS = 5  # 最多与模型往返几轮，防止无限循环

provider = os.getenv("LLM_PROVIDER") or "deepseek"
config = PROVIDERS[provider]
model = os.getenv("LLM_MODEL") or config["model"]
client = anthropic.Anthropic(
    api_key=os.getenv(config["key_env"]),
    base_url=config["base_url"],
)

# 告诉模型有哪些工具可用：名称、用途、参数格式（JSON Schema）
tools = [
    {
        "name": "get_weather",
        "description": "查询城市天气",
        "input_schema": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
    }
]


def get_weather(city):
    """工具的真实实现：这里用固定结果代替真实天气接口。"""
    return f"{city}：晴，22°C"


# 工具名 → 本地函数，用于按模型给出的名字找到要执行的函数
TOOL_FUNCTIONS = {"get_weather": get_weather}

# 对话历史：每一轮的提问、模型回复、工具结果都追加到这里
messages = [{"role": "user", "content": "上海今天天气怎么样？"}]
print(f"[配置] provider={provider} model={model}")

for turn in range(1, MAX_TURNS + 1):
    # 1) 把完整对话历史和工具清单发给模型，由模型决定：直接回答，还是调用工具
    resp = client.messages.create(
        model=model,
        max_tokens=1024,
        tools=tools,
        messages=messages,
    )
    # 模型的回复原样放回历史（其中可能包含思考块、文本块、工具调用块）
    messages.append({"role": "assistant", "content": resp.content})

    # 2) 不再请求工具，说明模型给出了最终回答：取出文本块并结束循环
    if resp.stop_reason != "tool_use":
        final_text = "".join([b.text for b in resp.content if b.type == "text"])
        print(f"[第 {turn} 轮] 最终回答：{final_text}")
        break

    # 3) 执行模型请求的每个工具，把结果按 tool_use_id 对应起来
    results = []
    for block in resp.content:
        if block.type == "tool_use":
            output = TOOL_FUNCTIONS[block.name](**block.input)
            print(f"[第 {turn} 轮] 调用工具 {block.name}({block.input}) -> {output}")
            results.append(
                {"type": "tool_result", "tool_use_id": block.id, "content": output}
            )

    # 4) 工具结果以 user 角色喂回模型，进入下一轮
    messages.append({"role": "user", "content": results})
else:
    # for 循环没有被 break（始终没拿到最终回答）时才会执行这里
    print(f"超过最大轮数 {MAX_TURNS}，仍未得到最终回答")
```

### 一句话概括

> 把“用户问题 + 工具说明书”发给模型；模型要么直接回答，要么请求调用工具；我们执行工具、把结果追加到对话历史再发回去；直到模型给出最终回答或达到 5 轮上限。

### 第 1–9 行：模块文档字符串

三引号字符串位于文件开头，是**模块文档字符串**（2.1）：说明用途、两种模型服务、运行命令（1.1）。

### 第 11–17 行：导入与加载 .env

| 行 | 代码 | 语法 / 课程 |
|---|---|---|
| 11 | `import os` | 导入标准库模块（5.1） |
| 13 | `import anthropic` | 导入第三方包，来自 `pyproject.toml` 依赖（1.2、5.1） |
| 14 | `from dotenv import load_dotenv` | 包名 `python-dotenv`，导入名 `dotenv`（1.2） |
| 17 | `load_dotenv()` | 读取 `.env` 写入 `os.environ`，默认不覆盖已有变量（8.3） |

### 第 20–32 行：配置常量

`PROVIDERS` 是两层 dict（4.2）：外层键选服务，内层键选字段；`None` 表示“使用 SDK 默认地址”（2.2）。全大写名字是约定的常量（2.1）。`MAX_TURNS = 5` 防止无限循环。

### 第 34–40 行：确定服务、模型，创建客户端

| 行 | 代码 | 要点 |
|---|---|---|
| 34 | `provider = os.getenv("LLM_PROVIDER") or "deepseek"` | `getenv` 缺失返回 `None`；`or` 让 `None` 和 `""` 都回退到默认值（2.2、8.3） |
| 35 | `config = PROVIDERS[provider]` | 下标访问，未知服务立即 `KeyError`（4.2、6.1） |
| 36 | `model = os.getenv("LLM_MODEL") or config["model"]` | 允许环境变量覆盖默认模型 |
| 37–40 | `client = anthropic.Anthropic(api_key=..., base_url=...)` | 调用类创建实例（7.1）；关键字参数（3.2）；嵌套调用由内向外读：`config["key_env"]` → `"DEEPSEEK_API_KEY"` → `os.getenv(...)` → 密钥 |

### 第 43–53 行：工具说明书

`tools` 是“dict 组成的 list”（4.1、4.2），**给模型看**：名称、用途、参数格式。`input_schema` 是 JSON Schema：参数是对象，`city` 为字符串且必填。模型据此决定是否调用、生成什么参数（8.2）。

### 第 56–62 行：工具实现与分发表

- `def get_weather(city)`：真正执行的 Python 函数，模型永远不会直接运行它（3.2）；返回 f-string（2.4）。
- `TOOL_FUNCTIONS = {"get_weather": get_weather}`：值是**函数对象**（不带括号），把模型给出的工具名（字符串）映射到本地函数（3.2）。

### 第 65–66 行：对话历史

`messages` 是 dict 组成的列表，每个 dict 是一条消息（4.1）。模型不保存上下文，每轮都要把完整历史发过去。

### 第 68–77 行：主循环与模型调用

- `for turn in range(1, MAX_TURNS + 1)`：`turn` 依次为 1–5（3.1）。
- `client.messages.create(...)`：属性链 + 方法调用（7.1、10.4）；`model`、`max_tokens`、`messages` 必填，SDK 中是仅限关键字参数（3.3）。
- 返回的 `resp` 是 `Message` 模型对象（7.3）：`resp.content` 是内容块对象列表，`resp.stop_reason` 是字符串（9.2）。
- 第 77 行把模型回复**原样**追加为 assistant 消息（4.1），这样下一轮模型能看到自己请求过什么工具。

### 第 80–83 行：终止条件

- `resp.stop_reason != "tool_use"`：模型不再请求工具，即给出了最终回答（3.1）。
- 第 81 行：列表推导式按 for → if → 表达式读：遍历块、只要文本块、取 `text`，再用 `""` 连接（4.4、2.3）。
- `break` 跳出 `for`，`else` 子句因此不执行（3.1）。

### 第 86–96 行：执行工具、回填结果

- 遍历 `resp.content`，只处理 `block.type == "tool_use"` 的块（一次回复可能请求多个工具）。
- 第 89 行核心：`TOOL_FUNCTIONS[block.name](**block.input)` = 查表得到函数 + 用 `**` 把参数字典展开为关键字参数（3.3）。
- `tool_result` 用 `tool_use_id` 对应到请求（模型据此知道哪个结果属于哪次调用）；工具结果以 **user** 角色发回，这是 Messages API 的约定。

### 第 97–99 行：循环的 else

与 `for` 对齐，只有 5 轮都没有 `break`（始终在请求工具）时才执行（3.1）。

### messages 的演变

| 时刻 | `messages` |
|---|---|
| 循环前 | `[user: 问题]` |
| 第 1 轮后 | `[user: 问题, assistant: [text?, tool_use get_weather], user: [tool_result]]` |
| 第 2 轮后 | 再追加 `assistant: [text 最终回答]`，然后 `break` |

部分模型（如开启思考模式时）还可能在 assistant 内容中返回 `thinking` 块（第 76 行注释也提到）；代码对它们不做处理，原样放回历史即可。

### 在浏览器中运行完整循环

真实 SDK 需要网络与密钥，无法在浏览器中运行。下面用一个**结构相同**的模拟客户端替换 `anthropic.Anthropic`：它看到“天气”就请求 `get_weather`，拿到工具结果后给出最终回答。配置与客户端换成模拟版本，循环部分与源文件第 32–99 行一致。试着修改：把问题换成“北京今天天气怎么样？”、把 `MAX_TURNS` 改成 `1`、让 `get_weather` 返回不同内容，观察输出与 `messages` 结构的变化。

```python run
from types import SimpleNamespace as NS

# ---------- 模拟的 anthropic 客户端（结构与真实 SDK 相同：client.messages.create → resp） ----------
class FakeMessages:
    TRIGGERS = {"get_weather": "天气", "get_time": "几点"}   # 问题中出现关键词才调用对应工具

    def create(self, *, model, max_tokens, tools, messages):
        last = messages[-1]["content"]
        if isinstance(last, str):                       # 用户提问 → 决定调用哪些工具
            city = next((c for c in ["上海", "北京", "深圳"] if c in last), "上海")
            calls = [
                NS(type="tool_use", id=f"toolu_{i:02d}", name=t["name"], input={"city": city})
                for i, t in enumerate(tools, 1)
                if self.TRIGGERS.get(t["name"], "\0") in last
            ]
            if calls:
                return NS(stop_reason="tool_use", content=[NS(type="text", text="我来查一下。"), *calls])
            return NS(stop_reason="end_turn", content=[NS(type="text", text="这个问题不需要工具。")])
        outputs = [r["content"] for r in last if r["type"] == "tool_result"]   # 拿到工具结果 → 最终回答
        return NS(stop_reason="end_turn", content=[NS(type="text", text="根据工具结果：" + "；".join(outputs))])


class FakeAnthropic:
    def __init__(self, api_key=None, base_url=None):
        self.messages = FakeMessages()

# ---------- 以下与 minimal_agent.py 第 32–99 行一致（client 换成模拟客户端） ----------
MAX_TURNS = 5
provider, model = "fake", "fake-model"
client = FakeAnthropic(api_key="sk-demo")

tools = [
    {
        "name": "get_weather",
        "description": "查询城市天气",
        "input_schema": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
    }
]


def get_weather(city):
    return f"{city}：晴，22°C"


TOOL_FUNCTIONS = {"get_weather": get_weather}

messages = [{"role": "user", "content": "上海今天天气怎么样？"}]
print(f"[配置] provider={provider} model={model}")

for turn in range(1, MAX_TURNS + 1):
    resp = client.messages.create(
        model=model,
        max_tokens=1024,
        tools=tools,
        messages=messages,
    )
    messages.append({"role": "assistant", "content": resp.content})

    if resp.stop_reason != "tool_use":
        final_text = "".join([b.text for b in resp.content if b.type == "text"])
        print(f"[第 {turn} 轮] 最终回答：{final_text}")
        break

    results = []
    for block in resp.content:
        if block.type == "tool_use":
            output = TOOL_FUNCTIONS[block.name](**block.input)
            print(f"[第 {turn} 轮] 调用工具 {block.name}({block.input}) -> {output}")
            results.append(
                {"type": "tool_result", "tool_use_id": block.id, "content": output}
            )

    messages.append({"role": "user", "content": results})
else:
    print(f"超过最大轮数 {MAX_TURNS}，仍未得到最终回答")

print("\n—— messages 最终结构 ——")
for i, m in enumerate(messages):
    content = m["content"] if isinstance(m["content"], str) else [getattr(b, "type", None) or b["type"] for b in m["content"]]
    print(i, m["role"], content)
```

## 易错点

- **以为模型会执行工具**：模型只返回“请调用 get_weather，参数 city=上海”；执行的是我们的代码（第 89 行）。
- **忘记把 assistant 回复放回历史**：下一轮模型看不到自己的 `tool_use` 请求，`tool_result` 无法对应，API 会报错。
- **`else` 属于 `if`**：看缩进，它与 `for` 对齐。
- **以为 `final_text` 一定非空**：若模型因 `max_tokens` 截断而停止且没有文本块，`final_text` 为空字符串；生产代码应检查 `stop_reason`。
- **工具名不在 `TOOL_FUNCTIONS` 中**：第 89 行抛 `KeyError`，整个程序退出（11.2 改造）。

## 对照

| 部分 | Python（本例） | JS（`@anthropic-ai/sdk`） |
|---|---|---|
| 创建客户端 | `anthropic.Anthropic(api_key=..., base_url=...)` | `new Anthropic({ apiKey, baseURL })` |
| 调用 | `client.messages.create(model=..., max_tokens=1024, ...)` | `await client.messages.create({ model, max_tokens: 1024, ... })` |
| 取文本 | `"".join([b.text for b in resp.content if b.type == "text"])` | `resp.content.filter(b => b.type === "text").map(b => b.text).join("")` |
| 执行工具 | `TOOL_FUNCTIONS[block.name](**block.input)` | `TOOL_FUNCTIONS[block.name](block.input)`（传整个对象） |
| 循环兜底 | `for … else` | 循环后用标志变量判断 |

## 读代码

不看注释，用 10.3 的四步法自查：

1. **入口与全貌**：顶层脚本，无 `main()`；主流程是第 68 行的 `for` 循环。
2. **核心数据**：`messages` 在第 65 行创建，第 77、96 行追加；`resp` 每轮重新赋值；`results` 每轮新建。
3. **名字来源**：`os`（标准库）、`anthropic` / `load_dotenv`（第三方）、`print` / `range`（内置），其余均在本文件定义。
4. **实验验证**：运行上面的模拟循环，或在本地执行 `uv run examples/agent/minimal_agent.py`（需要 `.env` 中的 `DEEPSEEK_API_KEY`）。

## 练习

### 练习 1：把循环封装为函数

把主循环封装为 `run_agent(client, question, tools, functions, max_turns=5)`：返回 `(final_text, messages)`；超过最大轮数时 `final_text` 为 `None`。检查会使用与上文相同的模拟客户端（已在起始代码中提供）。

```python exercise id=s11-l01-run-agent
# --- starter ---
from types import SimpleNamespace as NS

# ---------- 模拟的 anthropic 客户端（结构与真实 SDK 相同：client.messages.create → resp） ----------
class FakeMessages:
    TRIGGERS = {"get_weather": "天气", "get_time": "几点"}   # 问题中出现关键词才调用对应工具

    def create(self, *, model, max_tokens, tools, messages):
        last = messages[-1]["content"]
        if isinstance(last, str):                       # 用户提问 → 决定调用哪些工具
            city = next((c for c in ["上海", "北京", "深圳"] if c in last), "上海")
            calls = [
                NS(type="tool_use", id=f"toolu_{i:02d}", name=t["name"], input={"city": city})
                for i, t in enumerate(tools, 1)
                if self.TRIGGERS.get(t["name"], "\0") in last
            ]
            if calls:
                return NS(stop_reason="tool_use", content=[NS(type="text", text="我来查一下。"), *calls])
            return NS(stop_reason="end_turn", content=[NS(type="text", text="这个问题不需要工具。")])
        outputs = [r["content"] for r in last if r["type"] == "tool_result"]   # 拿到工具结果 → 最终回答
        return NS(stop_reason="end_turn", content=[NS(type="text", text="根据工具结果：" + "；".join(outputs))])


class FakeAnthropic:
    def __init__(self, api_key=None, base_url=None):
        self.messages = FakeMessages()


def run_agent(client, question, tools, functions, max_turns=5):
    messages = [{"role": "user", "content": question}]
    # 在这里实现循环
    return None, messages
# --- solution ---
from types import SimpleNamespace as NS

# ---------- 模拟的 anthropic 客户端（结构与真实 SDK 相同：client.messages.create → resp） ----------
class FakeMessages:
    TRIGGERS = {"get_weather": "天气", "get_time": "几点"}   # 问题中出现关键词才调用对应工具

    def create(self, *, model, max_tokens, tools, messages):
        last = messages[-1]["content"]
        if isinstance(last, str):                       # 用户提问 → 决定调用哪些工具
            city = next((c for c in ["上海", "北京", "深圳"] if c in last), "上海")
            calls = [
                NS(type="tool_use", id=f"toolu_{i:02d}", name=t["name"], input={"city": city})
                for i, t in enumerate(tools, 1)
                if self.TRIGGERS.get(t["name"], "\0") in last
            ]
            if calls:
                return NS(stop_reason="tool_use", content=[NS(type="text", text="我来查一下。"), *calls])
            return NS(stop_reason="end_turn", content=[NS(type="text", text="这个问题不需要工具。")])
        outputs = [r["content"] for r in last if r["type"] == "tool_result"]   # 拿到工具结果 → 最终回答
        return NS(stop_reason="end_turn", content=[NS(type="text", text="根据工具结果：" + "；".join(outputs))])


class FakeAnthropic:
    def __init__(self, api_key=None, base_url=None):
        self.messages = FakeMessages()


def run_agent(client, question, tools, functions, max_turns=5):
    messages = [{"role": "user", "content": question}]
    for turn in range(1, max_turns + 1):
        resp = client.messages.create(model="fake", max_tokens=1024, tools=tools, messages=messages)
        messages.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason != "tool_use":
            return "".join([b.text for b in resp.content if b.type == "text"]), messages
        results = []
        for block in resp.content:
            if block.type == "tool_use":
                output = functions[block.name](**block.input)
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": output})
        messages.append({"role": "user", "content": results})
    return None, messages
# --- check ---
TOOLS = [{"name": "get_weather", "description": "查询城市天气", "input_schema": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}]
FUNCS = {"get_weather": lambda city: f"{city}：晴，22°C"}
text, msgs = run_agent(FakeAnthropic(), "北京今天天气怎么样？", TOOLS, FUNCS)
assert text == "根据工具结果：北京：晴，22°C", text
assert [m["role"] for m in msgs] == ["user", "assistant", "user", "assistant"], [m["role"] for m in msgs]
assert msgs[2]["content"][0]["tool_use_id"] == "toolu_01"
text, msgs = run_agent(FakeAnthropic(), "北京今天天气怎么样？", TOOLS, FUNCS, max_turns=1)
assert text is None and len(msgs) == 3, "max_turns=1 时应在第 1 轮执行工具后结束并返回 None"
text, msgs = run_agent(FakeAnthropic(), "你好", TOOLS, FUNCS)
assert text == "这个问题不需要工具。" and len(msgs) == 2
```

### 练习 2：数一数

实现 `count_tool_calls(messages)`：统计对话历史中所有 assistant 消息里 `type == "tool_use"` 的块的总数。注意 user 消息的 `content` 可能是字符串，也可能是列表；assistant 的块是对象（用属性访问）。

```python exercise id=s11-l01-count
# --- starter ---
from types import SimpleNamespace as NS

def count_tool_calls(messages):
    return len(messages)
# --- solution ---
from types import SimpleNamespace as NS

def count_tool_calls(messages):
    return sum(
        1
        for m in messages
        if m["role"] == "assistant"
        for b in m["content"]
        if b.type == "tool_use"
    )
# --- check ---
msgs = [
    {"role": "user", "content": "问题"},
    {"role": "assistant", "content": [NS(type="text", text="查一下"), NS(type="tool_use"), NS(type="tool_use")]},
    {"role": "user", "content": [{"type": "tool_result"}, {"type": "tool_result"}]},
    {"role": "assistant", "content": [NS(type="tool_use")]},
    {"role": "user", "content": [{"type": "tool_result"}]},
    {"role": "assistant", "content": [NS(type="text", text="答案")]},
]
assert count_tool_calls(msgs) == 3, count_tool_calls(msgs)
assert count_tool_calls([{"role": "user", "content": "hi"}]) == 0
```

## 小结

- 循环骨架：发送历史 → 追加回复 → 无工具请求则结束 → 执行工具 → 追加结果 → 下一轮；`for … else` 兜底。
- 三个核心数据结构：`tools`（给模型的说明书）、`TOOL_FUNCTIONS`（名字 → 函数）、`messages`（不断增长的对话历史）。
- 核心一行 `TOOL_FUNCTIONS[block.name](**block.input)` 用到了 dict 下标、函数对象和 `**` 解包。

## 延伸阅读

- [更多控制流工具（for…else、** 解包）](https://docs.python.org/zh-cn/3/tutorial/controlflow.html)
- [数据结构（列表、字典、推导式）](https://docs.python.org/zh-cn/3/tutorial/datastructures.html)
- [类（属性与方法）](https://docs.python.org/zh-cn/3/tutorial/classes.html)
- [types.SimpleNamespace（模拟对象所用）](https://docs.python.org/zh-cn/3/library/types.html#types.SimpleNamespace)
