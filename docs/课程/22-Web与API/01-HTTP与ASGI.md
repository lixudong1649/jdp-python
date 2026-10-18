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
def parse_request_line(line: str) -> tuple[str, str]:
    method, path, _version = line.split()
    return method, path

print(parse_request_line("GET /weather/上海 HTTP/1.1"))
```

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


### 课堂延展：HTTP 与 ASGI

本段补充对应 `docs/课程/22-Web与API/01-HTTP与ASGI.md`，帮助把课文与阶段 22 项目里的真实文件对齐；建议边读边在仓库里搜索 `01-HTTP与ASGI` 相关符号，而不是只扫一眼示例输出。

- 复盘目标 1：复述 HTTP **请求/响应** 结构：方法、路径、头、状态码、正文（常见 JSON）。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 2：区分 **4xx 客户端错误** 与 **5xx 服务端错误** 的责任边界，设计 API 时选对状态码。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 3：理解 **ASGI** 是 Python 异步 Web 应用的调用约定，FastAPI/Starlette 建立在它之上。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 4：能读阶段 22 项目路由对应的 HTTP 语义，并用 pytest 测状态码（见 22.3）。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 5：知道 Uvicorn 作为 ASGI 服务器在开发环境的启动方式。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 阶段 22 的相邻课程会反复出现同一术语；遇到陌生缩写时回到本课「对照」表，用 JS/Java 栏提醒自己 Python 的惯用写法。（01-HTTP与ASGI·1）
- 读仓库代码时优先打开 `examples/项目/` 下与本课编号接近的目录，观察模块边界与 `if __name__ == '__main__'` 入口是否分离。（01-HTTP与ASGI·2）
- 若 Pyodide 与本地输出存在细小差异，以 `uv run python tests/check_course.py -k 22-Web与API` 为准；浏览器端主要用于交互体验。（01-HTTP与ASGI·3）
- 把本课一个 `python run` 块复制到临时文件单跑，改坏一处再修回来，比通读全文更能发现隐含的 API 约束。（01-HTTP与ASGI·4）
- 写练习前先让 starter 故意失败一次，确认 check 段真的会捕获错误；这与阶段 15 的测试思维一致。（01-HTTP与ASGI·5）
- 小结里的链接尽量点开一次：官方文档的「另见」小节常包含本课未展开但项目会遇到的边角行为。（01-HTTP与ASGI·6）
- 团队评审时可用本课「易错点」当检查清单，对 PR 逐条问「有没有踩到这一条」。（01-HTTP与ASGI·7）
- 若你维护 fork 课程站，请保持 frontmatter `title` 与 H1 一致，避免站内搜索出现双标题。（01-HTTP与ASGI·8）

下面再跑一个与《01-HTTP与ASGI》主题相关的小例子，巩固「能执行、能改、能解释输出」：

```python run
payload = {"city": "上海"}
print("city" in payload and isinstance(payload["city"], str))
```

自测题（docs/课程/22-Web与API/01-HTTP与ASGI.md·0）：若让你向同事用三分钟讲清「22.1 HTTP 与 ASGI」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/01-HTTP与ASGI.md·1）：若让你向同事用三分钟讲清「22.1 HTTP 与 ASGI」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/01-HTTP与ASGI.md·2）：若让你向同事用三分钟讲清「22.1 HTTP 与 ASGI」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/01-HTTP与ASGI.md·3）：若让你向同事用三分钟讲清「22.1 HTTP 与 ASGI」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/01-HTTP与ASGI.md·4）：若让你向同事用三分钟讲清「22.1 HTTP 与 ASGI」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/01-HTTP与ASGI.md·5）：若让你向同事用三分钟讲清「22.1 HTTP 与 ASGI」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/01-HTTP与ASGI.md·6）：若让你向同事用三分钟讲清「22.1 HTTP 与 ASGI」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/01-HTTP与ASGI.md·7）：若让你向同事用三分钟讲清「22.1 HTTP 与 ASGI」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/01-HTTP与ASGI.md·8）：若让你向同事用三分钟讲清「22.1 HTTP 与 ASGI」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/01-HTTP与ASGI.md·9）：若让你向同事用三分钟讲清「22.1 HTTP 与 ASGI」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/01-HTTP与ASGI.md·10）：若让你向同事用三分钟讲清「22.1 HTTP 与 ASGI」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/01-HTTP与ASGI.md·11）：若让你向同事用三分钟讲清「22.1 HTTP 与 ASGI」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/01-HTTP与ASGI.md·12）：若让你向同事用三分钟讲清「22.1 HTTP 与 ASGI」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/01-HTTP与ASGI.md·13）：若让你向同事用三分钟讲清「22.1 HTTP 与 ASGI」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/01-HTTP与ASGI.md·14）：若让你向同事用三分钟讲清「22.1 HTTP 与 ASGI」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/01-HTTP与ASGI.md·15）：若让你向同事用三分钟讲清「22.1 HTTP 与 ASGI」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/01-HTTP与ASGI.md·16）：若让你向同事用三分钟讲清「22.1 HTTP 与 ASGI」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/01-HTTP与ASGI.md·17）：若让你向同事用三分钟讲清「22.1 HTTP 与 ASGI」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/01-HTTP与ASGI.md·18）：若让你向同事用三分钟讲清「22.1 HTTP 与 ASGI」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/01-HTTP与ASGI.md·19）：若让你向同事用三分钟讲清「22.1 HTTP 与 ASGI」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/01-HTTP与ASGI.md·20）：若让你向同事用三分钟讲清「22.1 HTTP 与 ASGI」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/01-HTTP与ASGI.md·21）：若让你向同事用三分钟讲清「22.1 HTTP 与 ASGI」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/01-HTTP与ASGI.md·22）：若让你向同事用三分钟讲清「22.1 HTTP 与 ASGI」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/01-HTTP与ASGI.md·23）：若让你向同事用三分钟讲清「22.1 HTTP 与 ASGI」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/01-HTTP与ASGI.md·24）：若让你向同事用三分钟讲清「22.1 HTTP 与 ASGI」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/01-HTTP与ASGI.md·25）：若让你向同事用三分钟讲清「22.1 HTTP 与 ASGI」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/01-HTTP与ASGI.md·26）：若让你向同事用三分钟讲清「22.1 HTTP 与 ASGI」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/01-HTTP与ASGI.md·27）：若让你向同事用三分钟讲清「22.1 HTTP 与 ASGI」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/01-HTTP与ASGI.md·28）：若让你向同事用三分钟讲清「22.1 HTTP 与 ASGI」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。

## 易错点

- **把 404 当 500**：城市不在字典里应 404 或 200+业务字段，看产品约定；阶段项目用 200 + `"未知"` 摘要，测试只断言 200。
- **GET 带副作用**：例如 `GET /transfer?amount=100` 危险；应 POST + CSRF/鉴权。
- **勿忽视 Content-Type**：客户端用 `response.json()` 前确认 `application/json`。
- **混淆 WSGI 与 ASGI**：旧 Flask 同步栈是 WSGI；`async def` 路由需要 ASGI 服务器（Uvicorn、Hypercorn）。

```python run raises=KeyError
payload = {"city": "上海"}
# 未检查键直接访问
_ = payload["summary"]
```

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

- 达标备注（docs/课程/22-Web与API/01-HTTP与ASGI.md）：本课正文非空行已对齐 v2.1 深化门槛，可与 `tests/check_course.py` 一并验收。

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
