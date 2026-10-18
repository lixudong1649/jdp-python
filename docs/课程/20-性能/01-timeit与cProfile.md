---
title: 20.1 timeit 与 cProfile
---

# 20.1 timeit 与 cProfile

> 前置：18. 并发 · 约 25 分钟 · 官方对应：[timeit](https://docs.python.org/zh-cn/3/library/timeit.html)

## 目标

- 用 timeit 比较小段代码
- 知道 cProfile 看调用栈

## 核心概念

```python run
import timeit
print(timeit.timeit("sum(range(100))", number=10000) < 1.0)
```

## 易错点

- 微基准易受噪声影响。
- 先测再优化。

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 本节重点 | 见官方文档 | — | — |

## 读代码

怀疑慢函数时用 timeit/cProfile；不要凭感觉。

## 练习

```python exercise id=s20-l01-time
# --- starter ---
n = sum(range(9))
# --- solution ---
n = sum(range(10))
# --- check ---
assert n == 45
```

## 小结

- 测量先于优化
- timeit 重复多次

## 延伸阅读

- [timeit](https://docs.python.org/zh-cn/3/library/timeit.html)
