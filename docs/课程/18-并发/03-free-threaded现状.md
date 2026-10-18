---
title: 18.3 free-threaded 现状
---

# 18.3 free-threaded 现状

> 前置：18.1 threading · 约 25 分钟 · 官方对应：[What's New 3.14](https://docs.python.org/zh-cn/3/whatsnew/3.14.html)

## 目标

- 知道 3.14 起可选无 GIL 构建
- 默认发行版仍多线程 + GIL

## 核心概念

```python run
import sys
print(sys.version_info.major, sys.version_info.minor)
```

## 易错点

- free-threaded 与扩展 ABI 仍在演进。
- 生产选型以官方支持声明为准（核对日期 2026-10-18）。

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 本节重点 | 见官方文档 | — | — |

## 读代码

读性能文章时注意 Python 版本与是否 nogil；3.10 已 EOL。

## 练习

```python exercise id=s18-l03-ft
# --- starter ---
py = (3, 9)
# --- solution ---
py = (3, 12)
# --- check ---
assert py >= (3, 12)
```

## 小结

- 3.14 起官方提供 free-threaded
- 项目仍固定 3.12

## 延伸阅读

- [What's New 3.14](https://docs.python.org/zh-cn/3/whatsnew/3.14.html)
