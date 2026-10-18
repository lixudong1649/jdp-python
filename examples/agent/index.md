# 最小 Agent 循环示例

手写约 100 行的 Agent 循环，不依赖任何 Agent 框架，只用 Anthropic Messages API 的工具调用（tool use）能力。

## 循环原理

```text
messages = [用户提问]
重复最多 MAX_TURNS（5）轮：
    resp = 模型(messages, tools)       # 模型决定：直接回答，还是调用工具
    messages 追加 resp
    resp 不是 tool_use → 输出最终回答，结束
    results = 执行每个 tool_use        # 由我们的代码执行，不是模型执行
    messages 追加 results              # 结果喂回模型，进入下一轮
轮数用尽仍未结束 → 报告未完成
```

1. **模型决定**：把对话历史 `messages` 和工具清单 `tools` 发给模型，模型决定直接回答还是调用工具。
2. **本地执行**：模型只“请求”调用工具（给出工具名和参数），真正执行函数的是我们的代码。
3. **结果回填**：工具结果以 `tool_result` 块、`user` 角色追加到 `messages`，并用 `tool_use_id` 对应到请求。
4. **终止条件**：模型不再请求工具（得到最终回答），或达到最大轮数 `MAX_TURNS`。

## 模型服务切换

| `LLM_PROVIDER` | 端点 | 密钥变量 | 默认模型 |
|---|---|---|---|
| `deepseek`（默认） | `https://api.deepseek.com/anthropic`（DeepSeek 的 Anthropic 兼容端点） | `DEEPSEEK_API_KEY` | `deepseek-flash` |
| `anthropic` | Anthropic 官方 API | `ANTHROPIC_API_KEY` | `claude-haiku-4-5` |

- 可用 `LLM_MODEL` 覆盖默认模型名。
- 同一份 `anthropic` SDK 代码，仅 `base_url` 与 `api_key` 不同。
- Claude Pro 订阅不包含 API 额度；使用 `anthropic` 需 Anthropic Console 账户有余额。

## 运行

在项目根目录执行（依赖由 `uv` 根据 `pyproject.toml` / `uv.lock` 自动安装）：

```bash
cp .env.example .env          # 首次：填写 DEEPSEEK_API_KEY（.env 已被 git 忽略）
uv run examples/agent/minimal_agent.py
LLM_PROVIDER=anthropic uv run examples/agent/minimal_agent.py   # 切换到 Anthropic 官方 API
```

## 验证结果

2026-10-06，`deepseek` / `deepseek-flash` 实测输出（模型回答措辞每次可能不同）：

```text
[配置] provider=deepseek model=deepseek-flash
[第 1 轮] 调用工具 get_weather({'city': '上海'}) -> 上海：晴，22°C
[第 2 轮] 最终回答：上海今天天气：**晴**，气温 **22°C**。
...
```

`anthropic` 路径未实测（本机无 `ANTHROPIC_API_KEY`）。

## 限制

- `get_weather` 返回固定结果，仅演示循环机制。
- 未处理工具执行异常、未知工具名、网络错误；生产代码需补充。

## 延伸阅读

- 逐行语法解读：[docs/代码解读/minimal_agent.md](../../docs/代码解读/minimal_agent.md)
- 课程精读与改造练习：[11.1 逐行精读](../../docs/课程/11-简单项目/01-minimal_agent逐行精读.md)、[11.2 改造与自测](../../docs/课程/11-简单项目/02-改造与自测.md)
- [Anthropic 工具调用文档](https://docs.claude.com/en/docs/agents-and-tools/tool-use/overview)
- [DeepSeek Anthropic API 兼容说明](https://api-docs.deepseek.com/zh-cn/guides/anthropic_api)
