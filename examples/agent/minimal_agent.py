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
