---
title: 16.3 mypy 类型检查
---

# 16.3 mypy 类型检查

> 前置：9. 类型注解 · 约 25 分钟 · 官方对应：[mypy](https://mypy.readthedocs.io/en/stable/)

## 目标

- 运行 mypy 看静态类型错误
- 理解 typing 与运行时无关

## 核心概念

```python run
def greet(name: str) -> str:
    return f"hi, {name}"

print(greet("py"))
```

## 易错点

- Optional 与 `| None` 混用风格要统一。
- 第三方缺 stubs 时用 `# type: ignore` 谨慎。

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 本节重点 | 见官方文档 | — | — |

## 读代码

SDK 带完整类型；本地模块 gradual typing 逐步加注解。

## 练习

```python exercise id=s16-l03-mypy
# --- starter ---
def add(a, b):
    return str(a) + str(b)
# --- solution ---
def add(a: int, b: int) -> int:
    return a + b
# --- check ---
assert add(1, 2) == 3
```

## 小结

- mypy 静态分析
- 注解不改变运行时

## 延伸阅读

- [mypy 入门](https://mypy.readthedocs.io/en/stable/getting_started.html)
