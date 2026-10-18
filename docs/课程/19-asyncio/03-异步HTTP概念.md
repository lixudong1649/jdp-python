---
title: 19.3 异步 HTTP 概念
---

# 19.3 异步 HTTP 概念

> 前置：19.2 gather · 约 25 分钟 · 官方对应：[urllib](https://docs.python.org/zh-cn/3/library/urllib.request.html)

## 目标

- 理解 async 客户端与连接池
- 本课示例用标准库说明概念

## 核心概念

```python run
# async HTTP 客户端在本地项目 examples/项目/22 中演示；课内用常量模拟状态码
status = 200
print(status)
```

## 易错点

- 在 async 函数里调用阻塞 socket 会卡住事件循环。
- 生产用专用 async HTTP 客户端（见阶段 22）。

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 本节重点 | 见官方文档 | — | — |

## 读代码

读 SDK async 方法时看是否复用连接、是否需 `async with client`。

## 练习

```python exercise id=s19-l03-http
# --- starter ---
status = 404
# --- solution ---
status = 200
# --- check ---
assert status == 200
```

## 小结

- I/O 用 async 避免阻塞 loop
- HTTP 层见 Web 阶段

## 延伸阅读

- [urllib](https://docs.python.org/zh-cn/3/library/urllib.request.html)
