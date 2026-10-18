---
title: 阶段 18 · 并发
goal: 能按 I/O 或 CPU 密集选择 threading 或进程池
layer: L4
---

# 阶段 18 · 并发

**达成标志**：能按 I/O 或 CPU 密集选择 threading 或进程池。
阶段项目：[`examples/项目/18-并发下载模拟/downloader.py`](../../../examples/项目/18-并发下载模拟/downloader.py)（含 pytest）。

| 课程 | 你将学会 |
|---|---|
| [18.1 threading 与 GIL](01-threading与GIL.md) | 知道 GIL 限制 CPU 并行 |
| [18.2 multiprocessing 与 futures](02-multiprocessing与futures.md) | 用 ProcessPoolExecutor 并行 CPU 任务 |
| [18.3 free-threaded 现状](03-free-threaded现状.md) | 知道 3.14 起可选无 GIL 构建 |

前置：完成 v1 阶段 1–11；本阶段属 **L4**（核对日期 2026-10-18，正文对 Python 3.12–3.15 成立，项目固定 3.12）。
