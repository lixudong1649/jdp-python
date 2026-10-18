---
title: 16.2 ruff 静态检查
---

# 16.2 ruff 静态检查

> 前置：16.1 pyproject · 约 25 分钟 · 官方对应：[Ruff](https://docs.astral.sh/ruff/)

## 目标

- 会用 uv run ruff check
- 区分格式与 lint 规则

## 核心概念

```python run
# ruff 在 CI 中检查仓库 Python 代码；课内示例保持语法合法
x = 1 + 2
print(x)
```

## 易错点

- 自动 fix 可能改变语义，review diff。
- 与 formatter 规则冲突时以团队配置为准。

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 本节重点 | 见官方文档 | — | — |

## 读代码

提交前跑 ruff；读 `[tool.ruff]` 了解忽略项。

## 练习

```python exercise id=s16-l02-ruff
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

- ruff 速度快
- 配置在 pyproject

## 延伸阅读

- [Ruff linter](https://docs.astral.sh/ruff/linter/)
