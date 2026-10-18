---
title: 15.3 mock 与 monkeypatch
---

# 15.3 mock 与 monkeypatch

> 前置：15.2 fixture · 约 25 分钟 · 官方对应：[monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)

## 目标

- 用 monkeypatch 替换环境变量或函数
- 避免真实网络调用

## 核心概念

```python run
import os

def provider():
    return os.getenv("LLM_PROVIDER", "default")

os.environ["LLM_PROVIDER"] = "demo"
assert provider() == "demo"
```

## 易错点

- mock 过多导致测试与实现耦合。
- 记得恢复环境，pytest monkeypatch 会自动恢复。

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 本节重点 | 见官方文档 | — | — |

## 读代码

测 Agent 时用 fake client 替代 SDK；与 minimal_agent 的 PROVIDERS 思路一致。

## 练习

```python exercise id=s15-l03-mock
# --- starter ---
def always_true():
    return False
# --- solution ---
def always_true():
    return True
# --- check ---
assert always_true()
```

## 小结

- 隔离外部依赖
- monkeypatch 改 os.environ

## 延伸阅读

- [monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)
