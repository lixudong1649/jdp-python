---
title: 22.1 HTTP 与 ASGI
---

# 22.1 HTTP 与 ASGI

> 前置：19.3 异步 HTTP · 约 25 分钟 · 官方对应：[HTTP 概述](https://docs.python.org/zh-cn/3/library/http.html)

## 目标

- 理解请求/响应/status
- ASGI 是 async 应用协议

## 核心概念

```python run
from http import HTTPStatus
print(HTTPStatus.OK.value, HTTPStatus.NOT_FOUND.value)
```

## 易错点

- GET 不应有副作用。
- 5xx 与 4xx 责任不同。

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 本节重点 | 见官方文档 | — | — |

## 读代码

SDK REST 调用对应 HTTP；读 status_code 与 json()。

## 练习

```python exercise id=s22-l01-http
# --- starter ---
code = 404
# --- solution ---
code = 200
# --- check ---
assert code == 200
```

## 小结

- HTTP 语义
- ASGI 连接 async 框架

## 延伸阅读

- [http 模块](https://docs.python.org/zh-cn/3/library/http.html)
