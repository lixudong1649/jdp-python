# 读懂 minimal_agent.py

逐段解读 [examples/agent/minimal_agent.py](../../examples/agent/minimal_agent.py)，把每处语法对应到 [学习路线](../学习路线.md) 的阶段。循环原理与运行方式见 [examples/agent/README.md](../../examples/agent/README.md)。

> 本文是按语法分类的速查；按执行顺序的逐行精读、可运行模拟与练习见课程 [11.1 minimal_agent.py 逐行精读](../课程/11-简单项目/01-minimal_agent逐行精读.md)，改造练习见 [11.2 改造与自测](../课程/11-简单项目/02-改造与自测.md)。

> 行号以当前文件为准；修改代码后行号可能变化。

## 1. 语法速查

| 语法 | 代码中的例子（行号） | 含义 | 阶段 |
|---|---|---|---|
| 文档字符串 | `"""最小 Agent 循环示例……"""`（1–9） | 模块说明，三引号可跨行 | 2 |
| 注释 | `# 从项目根目录的 .env 读取……`（16） | `#` 之后到行尾不执行 | 2 |
| `import` | `import os`、`import anthropic`（11、13） | 导入整个模块，用 `模块.名字` 访问 | 5 |
| `from … import …` | `from dotenv import load_dotenv`（14） | 只导入模块中的某个名字，可直接使用 | 5 |
| dict 字面量 | `PROVIDERS = {"deepseek": {...}, ...}`（20–31） | 键值映射；可嵌套 | 4 |
| `None` | `"base_url": None`（27） | 表示“没有值” | 2 |
| 全大写常量 | `PROVIDERS`、`MAX_TURNS`、`TOOL_FUNCTIONS` | 约定为常量（PEP 8），语言本身不强制 | 10 |
| `or` 取默认值 | `os.getenv("LLM_PROVIDER") or "deepseek"`（34） | 左边为空（`None` 或 `""`）时取右边 | 2 |
| 下标访问 | `PROVIDERS[provider]`、`config["model"]`（35–36） | 按键取值；键不存在抛 `KeyError` | 4、6 |
| 关键字参数 | `anthropic.Anthropic(api_key=..., base_url=...)`（37–40） | 按参数名传参，顺序无关 | 3 |
| list 字面量 | `tools = [{...}]`（43–53） | 有序列表，元素可以是字典 | 4 |
| `def` / `return` | `def get_weather(city): return ...`（56–58） | 定义函数并返回结果 | 3 |
| f-string | `f"{city}：晴，22°C"`（58） | `{}` 内的表达式被求值后插入字符串 | 2 |
| 函数作为值 | `{"get_weather": get_weather}`（62） | 函数本身是对象，可存进字典（注意不带括号） | 3、7 |
| `for` + `range` | `for turn in range(1, MAX_TURNS + 1):`（68） | 依次取 1、2、3、4、5 | 3 |
| 属性访问 / 方法调用 | `client.messages.create(...)`、`resp.content`（70、77） | `.` 访问对象的属性或方法，可链式 | 7 |
| `list.append` | `messages.append({...})`（77、96） | 在列表末尾追加元素（原地修改） | 4 |
| `if` + `!=` | `if resp.stop_reason != "tool_use":`（80） | 条件不相等时执行缩进块 | 3 |
| 列表推导式 | `[b.text for b in resp.content if b.type == "text"]`（81） | 遍历 + 过滤 + 取值，生成新列表 | 4 |
| `str.join` | `"".join([...])`（81） | 用 `""` 把字符串列表拼成一个字符串 | 2 |
| `break` | （83） | 立即跳出 `for` 循环 | 3 |
| `**` 解包 | `TOOL_FUNCTIONS[block.name](**block.input)`（89） | 把字典展开成关键字参数 | 3 |
| `for … else` | `else:`（97） | 循环**未被 `break`** 正常跑完时才执行 | 3 |

## 2. 逐段解读

### 2.1 导入与配置（11–40）

```python
import os
import anthropic
from dotenv import load_dotenv
load_dotenv()
```

- `os` 是标准库，用于读取环境变量；`anthropic`、`dotenv` 是第三方包，由 `pyproject.toml` 声明、`uv` 安装。
- `load_dotenv()` 读取项目根目录 `.env`，把其中的 `KEY=VALUE` 放进环境变量，之后 `os.getenv("KEY")` 就能读到。

```python
provider = os.getenv("LLM_PROVIDER") or "deepseek"
config = PROVIDERS[provider]
model = os.getenv("LLM_MODEL") or config["model"]
```

- 三步决定“连哪家、用哪个模型”：读环境变量 → 查字典 → 允许覆盖。
- `PROVIDERS[provider]` 是两层字典的第一层，得到的 `config` 仍是字典，所以再用 `config["model"]` 取值。

```python
client = anthropic.Anthropic(api_key=os.getenv(config["key_env"]), base_url=config["base_url"])
```

- `anthropic.Anthropic` 是一个类，加括号调用即创建对象（实例）。
- 嵌套调用从内往外读：`config["key_env"]` 得到变量名 `"DEEPSEEK_API_KEY"` → `os.getenv(...)` 得到密钥 → 作为 `api_key` 传入。

### 2.2 工具声明与实现（43–62）

- `tools` 是**给模型看的说明书**：工具名、用途、参数格式（JSON Schema：参数 `city` 是字符串且必填）。模型据此决定是否调用、传什么参数。
- `get_weather` 是**真正执行的 Python 函数**。模型永远不会直接运行它。
- `TOOL_FUNCTIONS` 把两者连接起来：模型返回的工具名（字符串）→ 本地函数对象。

### 2.3 对话历史（65）

```python
messages = [{"role": "user", "content": "上海今天天气怎么样？"}]
```

- 列表里放字典，每个字典是一条消息。模型本身不记忆上下文，**每轮都要把完整历史发过去**。

### 2.4 主循环（68–99）

```python
for turn in range(1, MAX_TURNS + 1):
    resp = client.messages.create(model=model, max_tokens=1024, tools=tools, messages=messages)
    messages.append({"role": "assistant", "content": resp.content})
```

- `range(1, 6)` 不包含 6，所以最多 5 轮。
- `resp.content` 是一个“内容块”列表，每块有 `type` 属性：`"text"`（文本）、`"tool_use"`（工具调用请求），DeepSeek 默认还可能返回 `"thinking"`（思考过程）。整体原样追加回历史，下一轮模型才能接上。

```python
    if resp.stop_reason != "tool_use":
        final_text = "".join([b.text for b in resp.content if b.type == "text"])
        print(f"[第 {turn} 轮] 最终回答：{final_text}")
        break
```

- `stop_reason` 说明模型为何停下：`"tool_use"` 表示等待工具结果，其他值（如 `"end_turn"`）表示已给出回答。
- 列表推导式等价于：

  ```python
  texts = []
  for b in resp.content:
      if b.type == "text":
          texts.append(b.text)
  final_text = "".join(texts)
  ```

```python
    results = []
    for block in resp.content:
        if block.type == "tool_use":
            output = TOOL_FUNCTIONS[block.name](**block.input)
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": output})
    messages.append({"role": "user", "content": results})
```

- 核心一行 `TOOL_FUNCTIONS[block.name](**block.input)` 分三步读：
  1. `block.name` → `"get_weather"`
  2. `TOOL_FUNCTIONS["get_weather"]` → 函数 `get_weather`
  3. `(**{"city": "上海"})` → 等价于 `get_weather(city="上海")`
- `tool_use_id` 让模型知道每个结果对应哪次请求（一轮可能请求多个工具）。
- 工具结果以 `user` 角色发回，这是 Messages API 的约定。
- 这段显式循环等价于原始写法中的列表推导式 `results = [{...} for b in resp.content if b.type == "tool_use"]`；本例拆开是为了在执行时打印日志。

```python
else:
    print(f"超过最大轮数 {MAX_TURNS}，仍未得到最终回答")
```

- 这个 `else` 属于 `for`，不属于 `if`（看缩进对齐）：只有 5 轮都没有 `break` 时才执行。

## 3. 一次运行中 messages 的变化

| 时刻 | `messages` 内容 |
|---|---|
| 开始 | `[user: 提问]` |
| 第 1 轮后 | `[user: 提问, assistant: 请求 get_weather(city="上海"), user: tool_result "上海：晴，22°C"]` |
| 第 2 轮后 | 再追加 `assistant: 最终回答`，`break` 结束 |
