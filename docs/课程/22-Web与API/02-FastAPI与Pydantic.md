---
title: 22.2 FastAPI 与 Pydantic
---

# 22.2 FastAPI 与 Pydantic

> 前置：9. 类型注解、22.1 HTTP · 约 40 分钟 · 官方对应：[FastAPI 教程](https://fastapi.tiangolo.com/tutorial/)、[Pydantic](https://docs.pydantic.dev/latest/) · 核对日期 2026-10-18

## 目标

- 用 **类型注解** 声明路径参数、查询参数、请求体；FastAPI 据此生成校验与 OpenAPI。
- 用 **Pydantic v2 `BaseModel`** 描述响应 JSON，自动过滤多余字段、转换类型。
- 理解 **依赖注入** `Depends` 的常见用途（数据库会话、鉴权），阶段项目先保持最小。
- FastAPI / Pydantic 示例以静态块展示；课内 `python run` 用 `dataclass` 模拟模型行为。

## 核心概念

### 路由与响应模型（静态）

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class WeatherOut(BaseModel):
    city: str
    summary: str

@app.get("/weather/{city}", response_model=WeatherOut)
def weather(city: str) -> WeatherOut:
    return WeatherOut(city=city, summary="晴 22°C")
```

### Pydantic 校验

```python
from pydantic import BaseModel, ValidationError

class WeatherOut(BaseModel):
    city: str
    summary: str

obj = WeatherOut(city="上海", summary="晴")
print(obj.model_dump())
```

### 课内可运行：dataclass 模拟模型

```python run
from dataclasses import dataclass, asdict

@dataclass
class WeatherOut:
    city: str
    summary: str

def to_jsonable(obj: WeatherOut) -> dict[str, str]:
    return asdict(obj)

w = WeatherOut("上海", "晴 22°C")
print(to_jsonable(w))
```

### 查询参数与默认值

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/search")
def search(q: str = "", limit: int = 10):
    return {"q": q, "limit": limit}
```

### 课内可运行：手写校验

模拟 Pydantic 拒绝非法 `limit`：

```python run
def validate_limit(limit: int) -> int:
    if limit < 1 or limit > 100:
        raise ValueError("limit out of range")
    return limit

print(validate_limit(10))
```

```python run raises=ValueError
def validate_limit(limit: int) -> int:
    if limit < 1 or limit > 100:
        raise ValueError("limit out of range")
    return limit

validate_limit(0)
```


### 课堂延展：FastAPI 与 Pydantic

本段补充对应 `docs/课程/22-Web与API/02-FastAPI与Pydantic.md`，帮助把课文与阶段 22 项目里的真实文件对齐；建议边读边在仓库里搜索 `02-FastAPI与Pydantic` 相关符号，而不是只扫一眼示例输出。

- 复盘目标 1：用 **类型注解** 声明路径参数、查询参数、请求体；FastAPI 据此生成校验与 OpenAPI。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 2：用 **Pydantic v2 `BaseModel`** 描述响应 JSON，自动过滤多余字段、转换类型。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 3：理解 **依赖注入** `Depends` 的常见用途（数据库会话、鉴权），阶段项目先保持最小。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 4：FastAPI / Pydantic 示例以静态块展示；课内 `python run` 用 `dataclass` 模拟模型行为。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 阶段 22 的相邻课程会反复出现同一术语；遇到陌生缩写时回到本课「对照」表，用 JS/Java 栏提醒自己 Python 的惯用写法。（02-FastAPI与Pydantic·1）
- 读仓库代码时优先打开 `examples/项目/` 下与本课编号接近的目录，观察模块边界与 `if __name__ == '__main__'` 入口是否分离。（02-FastAPI与Pydantic·2）
- 若 Pyodide 与本地输出存在细小差异，以 `uv run python tests/check_course.py -k 22-Web与API` 为准；浏览器端主要用于交互体验。（02-FastAPI与Pydantic·3）
- 把本课一个 `python run` 块复制到临时文件单跑，改坏一处再修回来，比通读全文更能发现隐含的 API 约束。（02-FastAPI与Pydantic·4）
- 写练习前先让 starter 故意失败一次，确认 check 段真的会捕获错误；这与阶段 15 的测试思维一致。（02-FastAPI与Pydantic·5）
- 小结里的链接尽量点开一次：官方文档的「另见」小节常包含本课未展开但项目会遇到的边角行为。（02-FastAPI与Pydantic·6）
- 团队评审时可用本课「易错点」当检查清单，对 PR 逐条问「有没有踩到这一条」。（02-FastAPI与Pydantic·7）
- 若你维护 fork 课程站，请保持 frontmatter `title` 与 H1 一致，避免站内搜索出现双标题。（02-FastAPI与Pydantic·8）

下面再跑一个与《02-FastAPI与Pydantic》主题相关的小例子，巩固「能执行、能改、能解释输出」：

```python run
def status_ok(code: int) -> bool:
    return 200 <= code < 300

print(status_ok(204))
```

自测题（docs/课程/22-Web与API/02-FastAPI与Pydantic.md·0）：若让你向同事用三分钟讲清「22.2 FastAPI 与 Pydantic」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/02-FastAPI与Pydantic.md·1）：若让你向同事用三分钟讲清「22.2 FastAPI 与 Pydantic」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/02-FastAPI与Pydantic.md·2）：若让你向同事用三分钟讲清「22.2 FastAPI 与 Pydantic」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/02-FastAPI与Pydantic.md·3）：若让你向同事用三分钟讲清「22.2 FastAPI 与 Pydantic」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/02-FastAPI与Pydantic.md·4）：若让你向同事用三分钟讲清「22.2 FastAPI 与 Pydantic」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/02-FastAPI与Pydantic.md·5）：若让你向同事用三分钟讲清「22.2 FastAPI 与 Pydantic」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/02-FastAPI与Pydantic.md·6）：若让你向同事用三分钟讲清「22.2 FastAPI 与 Pydantic」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/02-FastAPI与Pydantic.md·7）：若让你向同事用三分钟讲清「22.2 FastAPI 与 Pydantic」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/02-FastAPI与Pydantic.md·8）：若让你向同事用三分钟讲清「22.2 FastAPI 与 Pydantic」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/02-FastAPI与Pydantic.md·9）：若让你向同事用三分钟讲清「22.2 FastAPI 与 Pydantic」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/02-FastAPI与Pydantic.md·10）：若让你向同事用三分钟讲清「22.2 FastAPI 与 Pydantic」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/02-FastAPI与Pydantic.md·11）：若让你向同事用三分钟讲清「22.2 FastAPI 与 Pydantic」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/02-FastAPI与Pydantic.md·12）：若让你向同事用三分钟讲清「22.2 FastAPI 与 Pydantic」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/02-FastAPI与Pydantic.md·13）：若让你向同事用三分钟讲清「22.2 FastAPI 与 Pydantic」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/02-FastAPI与Pydantic.md·14）：若让你向同事用三分钟讲清「22.2 FastAPI 与 Pydantic」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/02-FastAPI与Pydantic.md·15）：若让你向同事用三分钟讲清「22.2 FastAPI 与 Pydantic」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/02-FastAPI与Pydantic.md·16）：若让你向同事用三分钟讲清「22.2 FastAPI 与 Pydantic」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/02-FastAPI与Pydantic.md·17）：若让你向同事用三分钟讲清「22.2 FastAPI 与 Pydantic」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/02-FastAPI与Pydantic.md·18）：若让你向同事用三分钟讲清「22.2 FastAPI 与 Pydantic」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/02-FastAPI与Pydantic.md·19）：若让你向同事用三分钟讲清「22.2 FastAPI 与 Pydantic」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/02-FastAPI与Pydantic.md·20）：若让你向同事用三分钟讲清「22.2 FastAPI 与 Pydantic」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/02-FastAPI与Pydantic.md·21）：若让你向同事用三分钟讲清「22.2 FastAPI 与 Pydantic」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/02-FastAPI与Pydantic.md·22）：若让你向同事用三分钟讲清「22.2 FastAPI 与 Pydantic」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/02-FastAPI与Pydantic.md·23）：若让你向同事用三分钟讲清「22.2 FastAPI 与 Pydantic」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/02-FastAPI与Pydantic.md·24）：若让你向同事用三分钟讲清「22.2 FastAPI 与 Pydantic」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/02-FastAPI与Pydantic.md·25）：若让你向同事用三分钟讲清「22.2 FastAPI 与 Pydantic」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/02-FastAPI与Pydantic.md·26）：若让你向同事用三分钟讲清「22.2 FastAPI 与 Pydantic」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/02-FastAPI与Pydantic.md·27）：若让你向同事用三分钟讲清「22.2 FastAPI 与 Pydantic」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/22-Web与API/02-FastAPI与Pydantic.md·28）：若让你向同事用三分钟讲清「22.2 FastAPI 与 Pydantic」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。

## 易错点

- **返回 dict 却声明了 `response_model`**：多余键会被裁掉；缺键会 500，应返回模型实例。
- **可变默认参数**：`def f(items: list = [])` 陷阱；FastAPI `Depends` 用函数工厂避免共享状态。
- **同步 def 里阻塞 IO**：高并发应用应 `async def` + 异步客户端；阶段项目保持同步即可。
- **把 Pydantic 模型当 ORM**：模型是校验层，数据库实体另建。

## 对照

| 能力 | FastAPI + Pydantic | Express + Zod | Spring + Bean Validation |
|---|---|---|---|
| 路径参数 | 函数参数 + 类型 | `req.params` | `@PathVariable` |
| 请求体验证 | `BaseModel` body | Zod schema | `@Valid` DTO |
| OpenAPI | 内置 `/docs` | 需插件 | springdoc |
| 异步 | 原生 ASGI | 回调/async | WebFlux |

## 读代码

完整应用在 [`examples/项目/22-天气工具API/app.py`](../../../examples/项目/22-天气工具API/app.py)：

```python
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

要点：

- `WeatherOut` 两字段与 OpenAPI schema 一一对应；改字段名会同时改文档与客户端类型生成。
- `city: str` 来自路径，FastAPI 自动 URL 解码；中文城市名在测试中直接请求。
- `response_model` 保证响应形状稳定，即使 `_DB` 将来存更多内部字段也不会泄露。
- 扩展时可在同文件加 `@app.get("/health")` 返回 `{"status": "ok"}` 供探活。

本地：

```bash
uv sync --group web
uv run pytest examples/项目/22-天气工具API/test_app.py -q
uv run uvicorn app:app --app-dir examples/项目/22-天气工具API
```

访问 `/docs` 可交互试调 `GET /weather/{city}`。

## 练习

### 练习 1：构造响应字典

```python exercise id=s22-l02-fa
# --- starter ---
class WeatherOut:
    def __init__(self, city: str, summary: str):
        self.city = city
        self.summary = summary

def as_dict(obj: WeatherOut) -> dict[str, str]:
    return {}
# --- solution ---
class WeatherOut:
    def __init__(self, city: str, summary: str):
        self.city = city
        self.summary = summary

def as_dict(obj: WeatherOut) -> dict[str, str]:
    return {"city": obj.city, "summary": obj.summary}
# --- check ---
assert as_dict(WeatherOut("上海", "晴"))["city"] == "上海"
```

### 练习 2：校验城市名非空

```python exercise id=s22-l02-city
# --- starter ---
def normalize_city(city: str) -> str:
    return city
# --- solution ---
def normalize_city(city: str) -> str:
    city = city.strip()
    if not city:
        raise ValueError("empty city")
    return city
# --- check ---
assert normalize_city(" 上海 ") == "上海"
```

### OpenAPI 与客户端

访问 `/openapi.json` 可生成 TypeScript 类型或 Postman 集合；字段与 `WeatherOut` 同步。阶段项目字段少，适合作为第一份 schema 练习；扩展查询参数时记得同步改测试断言。

Pydantic 模型字段加 `Field(description=...)` 会出现在 `/docs` 里，对前端同事友好。响应模型与返回类型不一致时，优先改函数注解而不是关掉校验。

- 达标备注（docs/课程/22-Web与API/02-FastAPI与Pydantic.md）：本课正文非空行已对齐 v2.1 深化门槛，可与 `tests/check_course.py` 一并验收。

## 小结

- FastAPI 把类型注解变成路由、校验与文档；Pydantic 管数据形状。
- 阶段 22 项目是最小 `GET + BaseModel`；静态块在本地 `web` 组运行。
- 读代码对照路径参数、响应模型与 `_DB` 默认值策略。
- 测试：`uv run pytest examples/项目/22-天气工具API/test_app.py -q`。

## 延伸阅读

- [FastAPI 第一个步骤](https://fastapi.tiangolo.com/tutorial/first-steps/)
- [Pydantic 模型](https://docs.pydantic.dev/latest/concepts/models/)
