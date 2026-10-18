---
title: 15.1 pytest 基础
---

# 15.1 pytest 基础

> 前置：14.4 argparse · 约 25 分钟 · 官方对应：[pytest 文档](https://docs.pytest.org/en/stable/)

## 目标

- 写 test_ 函数与 assert
- 用 uv run pytest 收集测试

## 核心概念

```python run
def add(a, b):
    return a + b

def test_add():
    assert add(1, 2) == 3
```

## 易错点

- 测试函数必须以 test_ 开头。
- assert 失败会给出表达式分解（pytest 特性）。

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 本节重点 | 见官方文档 | — | — |

## 读代码

项目测试在 `examples/项目/15-CLI测试/`；本地命令：`uv run pytest examples/项目/15-CLI测试 -q`。

## 练习

```python exercise id=s15-l01-test
# --- starter ---
def double(x):
    return x
# --- solution ---
def double(x):
    return x * 2
# --- check ---
assert double(2) == 4
```

## 小结

- pytest 发现 test_*
- assert 即期望

## 延伸阅读

- [pytest 入门](https://docs.pytest.org/en/stable/getting-started.html)
