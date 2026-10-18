---
title: 17.1 wheel 与构建后端
---

# 17.1 wheel 与构建后端

> 前置：16.1 pyproject · 约 25 分钟 · 官方对应：[打包教程](https://packaging.python.org/en/latest/tutorials/packaging-project/)

## 目标

- 区分 wheel 与 sdist
- 知道 build 后端在 pyproject 声明

## 核心概念

```python run
# 构建在本地执行：uv build（课内仅示意命名）
name = "wheel"
print(name.endswith("heel"))
```

## 易错点

- 不要把 `.venv` 打进包。
- 版本号遵循 semver 习惯。

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 本节重点 | 见官方文档 | — | — |

## 读代码

安装依赖时 pip/uv 优先 wheel；读 Packaging 用户指南。

## 练习

```python exercise id=s17-l01-wheel
# --- starter ---
pkg = 'sdist'
# --- solution ---
pkg = 'wheel'
# --- check ---
assert pkg == 'wheel'
```

## 小结

- wheel 安装快
- sdist 需构建

## 延伸阅读

- [packaging 教程](https://packaging.python.org/en/latest/tutorials/packaging-project/)
