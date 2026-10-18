---
title: 15.2 fixture 与参数化
---

# 15.2 fixture 与参数化

> 前置：15.1 pytest 基础 · 约 25 分钟 · 官方对应：[fixture](https://docs.pytest.org/en/stable/explanation/fixtures.html)

## 目标

- 理解 fixture 注入
- 知道 @pytest.mark.parametrize 多组输入

## 核心概念

```python run
def sample():
    return [1, 2, 3]

def test_len():
    assert len(sample()) == 3
```

## 易错点

- fixture 作用域默认 function。
- parametrize 测试名会变长，注意可读性。

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 本节重点 | 见官方文档 | — | — |

## 读代码

 conftest.py 里共享 fixture；读测试先看参数名对应哪个 fixture。

## 练习

```python exercise id=s15-l02-fix
# --- starter ---
def upper(s):
    return s
# --- solution ---
def upper(s):
    return s.upper()
# --- check ---
assert upper('a') == 'A'
```

## 小结

- fixture 提供准备数据
- parametrize 减少重复用例

## 延伸阅读

- [fixtures](https://docs.pytest.org/en/stable/explanation/fixtures.html)
