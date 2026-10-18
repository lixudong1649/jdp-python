---
title: 21.3 Jupyter 工作流
---

# 21.3 Jupyter 工作流

> 前置：21.2 pandas · 约 25 分钟 · 官方对应：[JupyterLab](https://jupyter.org/documentation)

## 目标

- 知道 notebook 适合探索
- 最终逻辑仍应回到 .py 与测试

## 核心概念

```python run
print("notebook 在浏览器编辑；本仓库用 Markdown + Pyodide 课")
```

## 易错点

- notebook 难 code review。
- 输出顺序可能乱。

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 本节重点 | 见官方文档 | — | — |

## 读代码

探索数据用 Jupyter；交付用脚本与 pytest。

## 练习

```python exercise id=s21-l03-jup
# --- starter ---
mode = 'explore'
# --- solution ---
mode = 'script'
# --- check ---
assert mode == 'script'
```

## 小结

- Jupyter 交互探索
- 生产用模块+测试

## 延伸阅读

- [Jupyter 文档](https://jupyter.org/documentation)
