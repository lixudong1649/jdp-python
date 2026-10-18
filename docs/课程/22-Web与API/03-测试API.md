---
title: 22.3 测试 API
---

# 22.3 测试 API

> 前置：15. pytest · 约 25 分钟 · 官方对应：[TestClient](https://fastapi.tiangolo.com/tutorial/testing/)

## 目标

- 用 TestClient 不发真实网络
- 断言 status 与 JSON

## 核心概念

```python run
# 逻辑测试：模拟响应 dict
resp = {"city": "上海", "summary": "晴"}
assert resp["city"] == "上海"
```

## 易错点

- 测试应隔离数据库。
- 覆盖 404/422。

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 本节重点 | 见官方文档 | — | — |

## 读代码

与测 CLI 类似：调用函数/客户端，断言结构化输出。

## 练习

```python exercise id=s22-l03-api
# --- starter ---
resp = {}
# --- solution ---
resp = {'ok': True}
# --- check ---
assert resp['ok']
```

## 小结

- TestClient 同步测 async app
- 断言 schema

## 延伸阅读

- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
