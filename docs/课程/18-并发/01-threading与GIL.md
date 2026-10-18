---
title: 18.1 threading 与 GIL
---

# 18.1 threading 与 GIL

> 前置：3. 控制流 · 约 25 分钟 · 官方对应：[threading](https://docs.python.org/zh-cn/3/library/threading.html)

## 目标

- 知道 GIL 限制 CPU 并行
- I/O 阻塞时线程仍有用

## 核心概念

```python run
# Pyodide 中不宜演示真实线程；本地完整示例见 examples/项目/18-并发下载模拟/
import threading
print("threading 模块可用", threading.__name__)
```

## 易错点

- 多线程改同一 int 可能丢更新（非原子）。
- CPU 密集应用 multiprocessing 或 native 扩展。

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 本节重点 | 见官方文档 | — | — |

## 读代码

下载、等待 API 时常见线程/异步；读代码看阻塞点。

## 练习

```python exercise id=s18-l01-thread
# --- starter ---
import threading

lock = threading.Lock()
# --- solution ---
import threading

lock = threading.Lock()
acquired = lock.acquire(blocking=False)
lock.release()
# --- check ---
assert acquired
```

## 小结

- GIL 与 CPU 并行
- I/O 等待可线程

## 延伸阅读

- [threading](https://docs.python.org/zh-cn/3/library/threading.html)
