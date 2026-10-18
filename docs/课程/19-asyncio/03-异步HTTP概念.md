---
title: 19.3 异步 HTTP 概念
---

# 19.3 异步 HTTP 概念

> 前置：19.2 gather 与 TaskGroup · 约 30 分钟 · 官方对应：[urllib](https://docs.python.org/zh-cn/3/library/urllib.request.html)、[http.client](https://docs.python.org/zh-cn/3/library/http.client.html) · 核对日期 2026-10-18（标准库无官方 async HTTP 客户端；阶段 22 引入 FastAPI/httpx；课内用同步 urllib 讲清概念）

## 目标

- 理解 HTTP 客户端在 async 程序里的角色：**连接、请求、读响应体** 都应是可 await 的非阻塞步骤。
- 知道在 `async def` 里调用 **同步** `urllib` 会阻塞事件循环，应改用专用 async 客户端或 `asyncio.to_thread`。
- 了解连接复用、超时、状态码与异常分层（传输层 vs HTTP 4xx/5xx）。
- 把 `FakeAsyncClient` 与真实 SDK 的 `async with client` 模式对应起来。

## 核心概念

### 同步 HTTP：urllib 基线

标准库 `urllib.request.urlopen` 是阻塞调用，适合脚本，不适合放在高频 async 路由里。

```python run
import urllib.error
import urllib.request

def fetch_status_example() -> int:
    # 不访问外网：用 file:// 或构造逻辑；这里解析概念用常量模拟
    return 200

print(fetch_status_example() == 200)
```

真实外网请求在 CI 中不稳定；阶段 22 会在可控环境里演示 httpx。本课重点在 **调用模型**，不是特定域名。

### async 客户端应长什么样

典型模式（伪代码，本地项目阶段 22 实现）：

```python fragment
async with httpx.AsyncClient(timeout=10.0) as client:
    resp = await client.get("https://example.com")
    resp.raise_for_status()
    text = resp.text
```

要点：

- `AsyncClient` 持有 **连接池**；`async with` 确保关闭连接。
- `await client.get` 把等待时间交给事件循环。
- `raise_for_status()` 把 4xx/5xx 转成异常，与传输错误区分。

阶段 19 的 `FakeAsyncClient.complete` 是同一形状的缩小版：只有一个 `await` 点。

### 在 async 中包装阻塞 I/O

遗留同步 SDK 时，可用 `asyncio.to_thread(sync_fn, *args)`（3.9+）把阻塞调用丢进线程池，避免卡死循环——代价是线程开销，见 18.2。

课内用元数据表达「应用线程卸载」意图（不启动线程）：

```python run
import asyncio
import inspect

print(hasattr(asyncio, "to_thread"), inspect.iscoroutinefunction(asyncio.sleep))
```

### 超时与并发

多个 URL 并发时，常 `gather` 多个 `client.get`，每个带 `timeout`。某一请求挂起不应拖死全部（取决于客户端实现与 `gather` 选项）。

```python run
# 状态码分层：传输成功但业务错误
class HttpError(Exception):
    def __init__(self, status: int) -> None:
        self.status = status

def classify(status: int) -> str:
    if 200 <= status < 300:
        return "ok"
    if 400 <= status < 500:
        return "client"
    return "server"

print(classify(404), classify(502))
```


## 易错点

- **在 async 路由里直接 `urlopen`**：QPS 高时延迟飙升；用 async 客户端或 `to_thread`。
- **每次请求新建 TCP 连接**：慢；复用 `AsyncClient` 或会话对象。
- **忽略 SSL / 证书错误处理**：与同步相同，需显式配置或信任存储。
- **把 404 当传输异常**：HTTP 层应读 `status_code`，业务决定是否重试。

把整数当状态码对象使用会类型错误：

```python run raises=AttributeError
status = 200
print(status.ok)
```

## 对照

| 概念 | Python（async 生态） | JS | Java |
|---|---|---|---|
| 非阻塞客户端 | httpx/aiohttp（第三方） | `fetch` | Netty / `java.net.http` |
| 标准库阻塞 | `urllib.request` | 无（Node 有 http） | `HttpURLConnection` |
| 连接复用 | Client 实例 + 池 | Agent keep-alive | Connection pool |
| 超时 | `timeout=` 参数 | `AbortSignal` | `HttpTimeout` |
| 与 gather 组合 | `await gather(client.get(...), ...)` | `Promise.all` | `allOf` |

## 读代码

`FakeAsyncClient` 省略了 URL、方法、头与状态码，只保留 **await 边界**：

```python fragment
class FakeAsyncClient:
    async def complete(self, prompt: str) -> FakeResponse:
        await asyncio.sleep(0)
        return FakeResponse(text=f"echo:{prompt}")
```

- `complete` 对应真实 SDK 的 `POST /v1/chat/completions` 一类方法。
- `await asyncio.sleep(0)` 占位网络 RTT；真实客户端在 socket 可读时恢复。
- 返回 `FakeResponse` 而非裸 `str`，便于以后加 `status`、`headers` 字段。
- `run_once` 若并行多个 prompt，应对 `client.complete` 使用 `gather`（19.2）。

同步对比：若写成 `def complete(self, prompt): time.sleep(1); return ...`，在 async Agent 主循环里会 **冻结** 所有并发任务。

重试与退避（exponential backoff）在 async 客户端里通常用 `await asyncio.sleep(delay)` 实现，而不是 `time.sleep`；这样等待期间其它请求仍能推进。具体参数以 SDK 文档为准，本课只建立「等待也必须可 await」的意识。

响应体大小：流式下载可用 `aiter_bytes()`（第三方客户端常见 API）分块处理，避免一次性 `read()` 占满内存；这与同步 `urllib` 的 `read()` 一次性加载形成对比，读文档时留意 **streaming** 章节。

**分层记忆**：

- 传输层：TCP/TLS 连接是否建立、是否超时断开。
- HTTP 层：状态码、头字段、Content-Length / chunked。
- 应用层：JSON 解析、业务错误码、重试策略。
- async 层：上述每一步是否 `await`，是否共享 `AsyncClient` 连接池。

读 `FakeAsyncClient` 时，故意只有应用层 + async 层，便于先把 `await` 路径走通。

阶段 22 引入 FastAPI 与 httpx 后，请回来对照本课四层模型，看真实项目把超时、连接池、状态码分别放在哪一层配置。

本课练习用纯函数模拟 JSON 解析，避免课内依赖外网；这与生产环境「永远 mock 边界」的测试策略一致。

User-Agent、认证头、代理环境变量等属于 HTTP 客户端配置细节；阶段 22 会在可控示例里展开，本课只建立 async 调用形状。

`raise_for_status()` 之后仍要解析 JSON 并处理业务错误字段；HTTP 200 不代表业务成功。

同步 `urllib` 仍可用于健康检查脚本；async 服务路径应统一非阻塞客户端，避免混用两种风格。

连接池大小应与远端限流策略一致；过大并发可能触发 429 而非提升吞吐。

TLS 握手成本是复用连接的主要原因之一；这也是 `async with client` 生命周期管理的重要动机。

DNS 解析也可能阻塞；高级客户端会把解析与连接一并异步化，细节留在阶段 22。

重定向（3xx）与 Cookie  jar 行为在同步与 async 客户端中都应显式配置，避免安全与性能意外。

练习 `body_from_json` 模拟的是响应解析层；真实项目还会处理编码与 `Content-Type`。

完成阶段 19 后，你应能画出从 `run_once` 到多 URL `gather` 的调用示意图。

示意图不必复杂，能标出 `await` 边界即可。

## 练习

### 练习 1：判断是否成功状态码

实现 `is_success_status(code: int) -> bool`：200–299 返回 `True`。

```python exercise id=s19-l03-http
# --- starter ---
def is_success_status(code: int) -> bool:
    return False
# --- solution ---
def is_success_status(code: int) -> bool:
    return 200 <= code < 300
# --- check ---
assert is_success_status(200) is True
assert is_success_status(404) is False
assert is_success_status(299) is True
```

### 练习 2：从响应字典取正文

实现 `body_from_json(payload: dict) -> str`：若存在键 `"text"` 返回其字符串值；否则返回空字符串。模拟 JSON 响应解析（不写真实 HTTP）。

```python exercise id=s19-l03-body
# --- starter ---
def body_from_json(payload: dict) -> str:
    return "missing"
# --- solution ---
def body_from_json(payload: dict) -> str:
    val = payload.get("text")
    if isinstance(val, str):
        return val
    return ""
# --- check ---
assert body_from_json({"text": "hi"}) == "hi"
assert body_from_json({"other": 1}) == ""
assert body_from_json({}) == ""
```


## 小结

- async HTTP 的关键是 **可 await 的读写的整条链路**；同步 urllib 只适合线程卸载或脚本。
- 复用客户端实例、设置超时、区分传输错误与 HTTP 状态码。
- `FakeAsyncClient` 是阶段 22 真实 httpx 调用的预习形状。
- 并发多请求用 `gather` / TaskGroup，并注意失败传播策略。
- 标准库 `urllib` 适合同步脚本；async 服务应使用 async 客户端。
- 状态码与异常类型要分层处理，不要混为一谈。
- 连接池与超时是生产客户端的默认配置项，不是可选项。
- `FakeAsyncClient` 刻意省略 URL，让你先熟悉 `await` 形状。

## 延伸阅读

- [urllib.request 文档](https://docs.python.org/zh-cn/3/library/urllib.request.html)
- [http.client — HTTP 协议低层](https://docs.python.org/zh-cn/3/library/http.client.html)
