---
title: 22.2 FastAPI 与 Pydantic
---

# 22.2 FastAPI 与 Pydantic

> 前置：9. 类型注解 · 约 25 分钟 · 官方对应：[FastAPI 教程](https://fastapi.tiangolo.com/tutorial/)

## 目标

- 路由函数返回模型
- Pydantic 校验请求/响应

## 核心概念

```python run
# FastAPI 在本地 examples/项目/22；课内用 dataclass 模拟模型
from dataclasses import dataclass

@dataclass
class WeatherOut:
    city: str
    summary: str

print(WeatherOut("上海", "晴"))
```

## 易错点

- 依赖注入在 FastAPI 很常见。
- 自动 OpenAPI 文档。

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 本节重点 | 见官方文档 | — | — |

## 读代码

写 API 与读 SDK 相反：你定义 schema；仍用类型注解。

## 练习

```python exercise id=s22-l02-fa
# --- starter ---
class M:
    pass
# --- solution ---
class M:
    def __init__(self, x):
        self.x = x
# --- check ---
assert M(1).x == 1
```

## 小结

- FastAPI 基于类型提示
- Pydantic v2 校验

## 延伸阅读

- [FastAPI](https://fastapi.tiangolo.com/tutorial/)
- [Pydantic](https://docs.pydantic.dev/latest/)
