---
title: 18.2 multiprocessing 与 futures
---

# 18.2 multiprocessing 与 futures

> 前置：18.1 threading · 约 25 分钟 · 官方对应：[concurrent.futures](https://docs.python.org/zh-cn/3/library/concurrent.futures.html)

## 目标

- 用 ProcessPoolExecutor 并行 CPU 任务
- 用 ThreadPoolExecutor 并行 I/O

## 核心概念

```python run
from concurrent.futures import ThreadPoolExecutor
print("ThreadPoolExecutor", ThreadPoolExecutor)
```

## 易错点

- 子进程启动开销大。
- 传递对象需可 pickle。

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 本节重点 | 见官方文档 | — | — |

## 读代码

批量请求 SDK 时可能用线程池；读 `max_workers` 与 map 语义。

## 练习

```python exercise id=s18-l02-pool
# --- starter ---
pool = type('Pool', (), {'__name__': 'Wrong'})()
# --- solution ---
from concurrent.futures import ThreadPoolExecutor

pool = ThreadPoolExecutor
# --- check ---
assert pool.__name__ == 'ThreadPoolExecutor'
```

## 小结

- Executor 统一接口
- map 保序收集

## 延伸阅读

- [concurrent.futures](https://docs.python.org/zh-cn/3/library/concurrent.futures.html)
