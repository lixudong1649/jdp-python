---
title: 16.1 src 布局与 pyproject
---

# 16.1 src 布局与 pyproject

> 前置：5.2 包与项目结构 · 约 25 分钟 · 官方对应：[pyproject](https://packaging.python.org/en/latest/specifications/pyproject-toml/)

## 目标

- 读懂 pyproject 的 project 与 dependency-groups
- 知道 src 布局避免 import 污染

## 核心概念

```python run
sample = '[project]\nname = "demo"\n'
print(sample.startswith("["))
```

## 易错点

-  editable 安装与 plain 脚本布局不同。
- 锁文件 uv.lock 应与 pyproject 一致。

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 本节重点 | 见官方文档 | — | — |

## 读代码

本仓库 `uv run` 读取 pyproject；读依赖先看 `[project]` 与 `[dependency-groups]`。

## 练习

```python exercise id=s16-l01-toml
# --- starter ---
name = 'demo'
# --- solution ---
name = 'demo'
version = '0.0.1'
# --- check ---
assert version == '0.0.1'
```

## 小结

- pyproject 是项目清单
- uv 管理锁与组

## 延伸阅读

- [pyproject 规范](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
- [uv 项目](https://docs.astral.sh/uv/guides/projects/)
