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


## 小结

- FastAPI 把类型注解变成路由、校验与文档；Pydantic 管数据形状。
- 阶段 22 项目是最小 `GET + BaseModel`；静态块在本地 `web` 组运行。
- 读代码对照路径参数、响应模型与 `_DB` 默认值策略。
- 测试：`uv run pytest examples/项目/22-天气工具API/test_app.py -q`。

## 延伸阅读

- [FastAPI 第一个步骤](https://fastapi.tiangolo.com/tutorial/first-steps/)
- [Pydantic 模型](https://docs.pydantic.dev/latest/concepts/models/)
