---
title: 12.4 ABC 与 Protocol
---

# 12.4 ABC 与 Protocol

> 前置：9.2 typing 进阶 · 约 25 分钟 · 官方对应：[abc 模块](https://docs.python.org/zh-cn/3/library/abc.html)

## 目标

- 用 ABC 声明必须实现的方法
- 用 `typing.Protocol` 做结构化子类型（3.8 起稳定）

## 核心概念

```python run
from typing import Protocol

class SupportsLen(Protocol):
    def __len__(self) -> int: ...

def report_size(obj: SupportsLen) -> int:
    return len(obj)

print(report_size([1, 2, 3]))
```

## 易错点

- ABC 子类未实现抽象方法无法实例化。
- Protocol 只在类型检查时生效，运行时不强制。

## 对照

| | Python | JS | Java |
|---|---|---|---|
| 接口 | Protocol / ABC | TS interface | interface |

## 读代码

读 SDK 时常见 `Protocol` 或抽象基类约束客户端实现；静态类型帮助，运行时仍靠 duck typing。

## 练习

```python exercise id=s12-l04-proto
# --- starter ---
from typing import Protocol

class Runner(Protocol):
    def run(self) -> str: ...
# --- solution ---
from typing import Protocol

class Runner(Protocol):
    def run(self) -> str: ...

class Job:
    def run(self) -> str:
        return "ok"

def go(r: Runner) -> str:
    return r.run()
# --- check ---
assert go(Job()) == "ok"
```

## 小结

- Protocol 描述能力而非继承
- ABC 适合强制子类实现

## 延伸阅读

- [typing.Protocol](https://docs.python.org/zh-cn/3/library/typing.html#typing.Protocol)
- [abc](https://docs.python.org/zh-cn/3/library/abc.html)
