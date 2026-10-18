---
title: 13.4 match 语句
---

# 13.4 match 语句

> 前置：3.1 条件与循环 · 约 25 分钟 · 官方对应：[match 语句](https://docs.python.org/zh-cn/3/reference/compound_stmts.html#the-match-statement)（3.10 起）

## 目标

- 用 match/case 做结构化分支
- 结合序列模式与字面量

## 核心概念

```python run
def kind(x):
    match x:
        case {"type": "text", "text": t}:
            return f"text:{t}"
        case {"type": name}:
            return f"other:{name}"
        case _:
            return "unknown"

print(kind({"type": "text", "text": "hi"}))
```

## 易错点

- case 顺序从上到下匹配。
- 不要用 match 替代简单 if 导致可读性下降。

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 本节重点 | 见官方文档 | — | — |

## 读代码

读消息块时可 match `block.type`；与 if/elif 等价但模式更清晰。

## 练习

```python exercise id=s13-l04-match
# --- starter ---
def label(x):
    return 'x'
# --- solution ---
def label(x):
    match x:
        case 1:
            return 'one'
        case _:
            return 'other'
# --- check ---
assert label(1) == 'one' and label(2) == 'other'
```

## 小结

- match 3.10 起可用
- 模式可解构 dict

## 延伸阅读

- [match 语句](https://docs.python.org/zh-cn/3/reference/compound_stmts.html#the-match-statement)
