---
title: 22.1 HTTP 与 ASGI
---

# 22.1 HTTP 与 ASGI

> 前置：19.3 异步 HTTP、8.2 JSON · 约 35 分钟 · 官方对应：[http 模块](https://docs.python.org/zh-cn/3/library/http.html) · 核对日期 2026-10-18

## 目标

- 复述 HTTP **请求/响应** 结构：方法、路径、头、状态码、正文（常见 JSON）。
- 区分 **4xx 客户端错误** 与 **5xx 服务端错误** 的责任边界，设计 API 时选对状态码。
- 理解 **ASGI** 是 Python 异步 Web 应用的调用约定，FastAPI/Starlette 建立在它之上。
- 能读阶段 22 项目路由对应的 HTTP 语义，并用 pytest 测状态码（见 22.3）。
- 知道 Uvicorn 作为 ASGI 服务器在开发环境的启动方式。

## 核心概念

### 状态码与语义

```python run
from http import HTTPStatus

def classify(code: int) -> str:
    if 200 <= code < 300:
        return "success"
    if 400 <= code < 500:
        return "client"
    if 500 <= code < 600:
        return "server"
    return "other"

print(HTTPStatus.OK.value, classify(200))
print(HTTPStatus.NOT_FOUND.value, classify(404))
print(HTTPStatus.INTERNAL_SERVER_ERROR.value, classify(500))
```

### 请求行与方法

GET 应幂等、无副作用；POST 创建资源；PUT/PATCH 更新。课内用纯数据结构模拟“解析结果”。

```python run
from urllib.parse import unquote

SAMPLES = [
    "GET /weather/%E4%B8%8A%E6%B5%B7 HTTP/1.1",
    "POST /reports HTTP/1.1",
    "DELETE /session/abc HTTP/1.1",
]
SAFE = {"GET", "HEAD", "POST", "PUT", "PATCH", "DELETE"}


def parse_request_line(line: str) -> tuple[str, str, str]:
    method, raw_path, version = line.split()
    if method not in SAFE:
        raise ValueError(f"unsupported method {method}")
    path = unquote(raw_path)
    return method, path, version


for raw in SAMPLES:
    method, path, ver = parse_request_line(raw)
    idempotent = method in {"GET", "HEAD", "PUT", "DELETE"}
    print(raw)
    print("  ->", method, path, ver, "幂等/安全读?", idempotent)
```

请求行拆成方法、解码后的路径与版本，并标注常见方法是否幂等。浏览器里 `%E4%B8%8A%E6%B5%B7` 会变成可读的中文路径，这与 ASGI `scope["path"]` 里看到的一致。

### 响应体与 JSON

API 常返回 JSON；Python 侧用 `json.dumps` / `json.loads` 与类型注解配合（FastAPI 在 22.2 用 Pydantic 自动完成）。

```python run
import json

body = {"city": "上海", "summary": "晴 22°C"}
raw = json.dumps(body, ensure_ascii=False)
back = json.loads(raw)
assert back["city"] == "上海"
print(raw)
```

### ASGI 三元组（概念）

ASGI 应用是可调用的 `async def app(scope, receive, send)`：`scope` 含 `type=http`、路径、方法；`receive` 读 body；`send` 写响应。FastAPI 帮你生成这一层；静态示意：

```python
# 极简 ASGI 概念（本地阅读，不运行）
async def app(scope, receive, send):
    assert scope["type"] == "http"
    await send({"type": "http.response.start", "status": 200, "headers": []})
    await send({"type": "http.response.body", "body": b"ok"})
```

本地跑阶段 22 服务（需 `web` 依赖组）：

```bash
uv sync --group web
uv run uvicorn app:app --app-dir examples/项目/22-天气工具API --reload
```

浏览器访问 `http://127.0.0.1:8000/weather/上海` 应看到 JSON。开发时 `--reload` 改代码自动重启。


## 易错点

- **把 404 当 500**：城市不在字典里应 404 或 200+业务字段，看产品约定；阶段项目用 200 + `"未知"` 摘要，测试只断言 200。
- **GET 带副作用**：例如 `GET /transfer?amount=100` 危险；应 POST + CSRF/鉴权。
- **勿忽视 Content-Type**：客户端用 `response.json()` 前确认 `application/json`。
- **混淆 WSGI 与 ASGI**：旧 Flask 同步栈是 WSGI；`async def` 路由需要 ASGI 服务器（Uvicorn、Hypercorn）。

```python run raises=KeyError
payload = {"city": "上海", "updated_at": "2026-10-19T08:00:00Z"}
required = ("city", "summary", "updated_at")
print("响应体键", list(payload.keys()))
for key in required:
    present = key in payload
    print(key, "存在?", present)
missing = [k for k in required if k not in payload]
print("缺字段", missing, "仍直接取 summary")
_ = payload["summary"]
```

客户端假设 OpenAPI 里声明的 `summary` 一定存在，但后端只回了城市与时间戳；打印键清单后仍用 `payload["summary"]` 会 `KeyError`。生产代码应改用 `.get()` 或 Pydantic 模型校验。

## 对照

| 概念 | Python 生态 | Node.js | Java |
|---|---|---|---|
| HTTP 客户端 | `httpx` / `urllib` | `fetch` | `HttpClient` |
| 异步服务接口 | ASGI | 回调 / `http.Server` | Servlet / reactive |
| 路由框架 | FastAPI, Starlette | Express, Fastify | Spring MVC |
| 本地开发服务器 | Uvicorn | `node --watch` | embedded Tomcat |

## 读代码

阶段 22 [`app.py`](../../../examples/项目/22-天气工具API/app.py) 把 HTTP GET 映射到 Python 函数：

```python
"""最小 FastAPI 天气 API（阶段 22，内存数据）。"""
from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
_DB = {"上海": "晴 22°C", "北京": "多云 18°C"}


class WeatherOut(BaseModel):
    city: str
    summary: str


@app.get("/weather/{city}", response_model=WeatherOut)
def weather(city: str) -> WeatherOut:
    summary = _DB.get(city, "未知")
    return WeatherOut(city=city, summary=summary)
```

读法：

1. `@app.get("/weather/{city}")` 声明路径模板；`city` 从 URL 段注入，等价 HTTP `GET /weather/上海`。
2. `response_model=WeatherOut` 约束响应 JSON 字段，OpenAPI 文档自动生成。
3. `_DB` 是内存假数据；真实项目换 Redis/HTTP 上游，**路由签名可不变**。
4. `summary = _DB.get(city, "未知")` 避免 KeyError，属于业务层默认值，不是 HTTP 404。
5. 返回 `WeatherOut` 实例，FastAPI 序列化为 `{"city":"...","summary":"..."}`。

测试（不启真实端口）：

```bash
uv sync --group web
uv run pytest examples/项目/22-天气工具API/test_app.py -q
```

## 练习

### 练习 1：判断状态码类别

```python exercise id=s22-l01-http
# --- starter ---
def is_client_error(code: int) -> bool:
    return False
# --- solution ---
def is_client_error(code: int) -> bool:
    return 400 <= code < 500
# --- check ---
assert is_client_error(404)
assert not is_client_error(200)
```

### 练习 2：组装 JSON 响应字典

实现 `weather_json(city: str, summary: str) -> dict[str, str]`，键为 `city` 与 `summary`。

```python exercise id=s22-l01-json
# --- starter ---
def weather_json(city: str, summary: str) -> dict[str, str]:
    return {}
# --- solution ---
def weather_json(city: str, summary: str) -> dict[str, str]:
    return {"city": city, "summary": summary}
# --- check ---
assert weather_json("上海", "晴")["summary"] == "晴"
```

### 本地联调清单

启动 Uvicorn 后，用浏览器或 `curl` 访问 `/weather/上海`；对照响应头 `content-type` 是否含 `json`。改 `_DB` 文案后无需重启测试客户端用例，但手工联调需刷新页面。记录核对日期 2026-10-18 时使用的 FastAPI 版本，便于日后升级对照 OpenAPI 变化。

REST 路径尽量用名词复数或资源名，动词放在 HTTP 方法里；阶段项目用 `/weather/{city}` 是资源导向示例。日志里同时打印 method、path、status 三件套，排障时比只看 body 更快。

缓存头 `Cache-Control` 与 API 动态数据常冲突；天气类读多写少接口才适合短缓存。


## 小结

- HTTP 语义是 Web API 的契约；状态码表达谁错了。
- ASGI 连接异步 Python 与 Uvicorn；FastAPI 路由是语法糖。
- 读 `app.py` 时对照 URL、响应模型与内存数据源。
- 验证：`uv run pytest examples/项目/22-天气工具API/test_app.py -q`。
- HEAD 请求可探活而不拉 body。
- PUT 全量替换与 PATCH 部分更新语义不同，设计 API 时写进文档。
- CORS 由浏览器强制执行，服务端需显式允许源。
- HTTPS 终止常在反向代理，Uvicorn 前可加 Nginx。
- 核对日期 2026-10-18：HTTP/2 常由代理处理，应用层仍写 HTTP/1.1 语义。
- 阶段项目无鉴权，扩展时再加 Bearer 或 Cookie。
- OPTIONS 预检与 CORS 相关，前后端分离时要配置。
- 请求 ID 头便于分布式追踪，微服务阶段再深入。
- 超时在客户端与服务端都要设置，避免挂死连接。
- 健康检查路径 `/health` 与业务路由分开，便于探针。
- 核对日期 2026-10-18：课程示例端口 8000 仅本地开发使用。

## 延伸阅读

- [http — HTTP 状态码](https://docs.python.org/zh-cn/3/library/http.html#http.HTTPStatus)
- [FastAPI 部署与 Uvicorn](https://fastapi.tiangolo.com/deployment/)
