---
title: 16.4 logging 配置与 pdb
---

# 16.4 logging 配置与 pdb

> 前置：8.6 logging · 约 25 分钟 · 官方对应：[logging](https://docs.python.org/zh-cn/3/library/logging.html)

## 目标

- 配置 basicConfig 或 dictConfig
- 会用 pdb 断点调试

## 核心概念

```python run
import logging
logging.basicConfig(level=logging.INFO)
logging.info("ready")
```

## 易错点

- root logger 多次 basicConfig 可能无效。
- 生产环境用结构化日志而非 print。

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 本节重点 | 见官方文档 | — | — |

## 读代码

minimal_agent 可改为 logging；读配置看 level 与 handler。

## 练习

```python exercise id=s16-l04-log
# --- starter ---
def log_msg():
    pass
# --- solution ---
def log_msg():
    return 'info'
# --- check ---
assert log_msg() == 'info'
```

## 小结

- logging 分级
- pdb 适合本地交互

## 延伸阅读

- [logging HOWTO](https://docs.python.org/zh-cn/3/howto/logging.html)
