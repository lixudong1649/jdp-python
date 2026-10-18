---
title: 21.1 NumPy 入门
---

# 21.1 NumPy 入门

> 前置：2.2 数字 · 约 25 分钟 · 官方对应：[NumPy 用户指南](https://numpy.org/doc/stable/user/index.html)

## 目标

- 知道 ndarray 与向量化
- 示例在本地项目运行

## 核心概念

```python run
# 课内 Pyodide 无 NumPy；用纯 Python 模拟向量加法
a = [1, 2, 3]
b = [4, 5, 6]
print([x + y for x, y in zip(a, b)])
```

## 易错点

- NumPy 数组与 list 不同。
- 广播规则易错，需查文档。

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 本节重点 | 见官方文档 | — | — |

## 读代码

数据分析栈底层 NumPy；pandas Series 基于 ndarray。

## 练习

```python exercise id=s21-l01-np
# --- starter ---
a = [1]
b = [2]
vec = [0]
# --- solution ---
a = [1]
b = [2]
vec = [x+y for x,y in zip(a,b)]
# --- check ---
assert vec == [3]
```

## 小结

- 向量化避免 Python 循环
- 本地 uv sync --group data

## 延伸阅读

- [NumPy 文档](https://numpy.org/doc/stable/)
