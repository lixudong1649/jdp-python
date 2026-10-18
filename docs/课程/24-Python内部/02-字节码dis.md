---
title: 24.2 字节码 dis
---

# 24.2 字节码 dis

> 前置：3.2 函数 · 约 25 分钟 · 官方对应：[dis 模块](https://docs.python.org/zh-cn/3/library/dis.html)

## 目标

- 会用 dis.dis 看 opcode
- 理解 LOAD/STORE/CALL

## 核心概念

```python run
import dis

def add(a, b):
    return a + b

dis.dis(add)
print("shown")
```

## 易错点

- 字节码因版本而异。
- 仅调试/原理用，日常不必背 opcode。

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 本节重点 | 见官方文档 | — | — |

## 读代码

性能极热点才看字节码；读怪行为先查数据模型。

## 练习

```python exercise id=s24-l02-dis
# --- starter ---
def f():
    return 0
# --- solution ---
def f():
    return 1
# --- check ---
assert f() == 1
```

## 小结

- dis 展示栈机指令
- CPython 实现细节

## 延伸阅读

- [dis](https://docs.python.org/zh-cn/3/library/dis.html)
