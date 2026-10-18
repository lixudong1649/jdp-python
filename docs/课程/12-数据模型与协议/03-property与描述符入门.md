---
title: 12.3 property 与描述符入门
---

# 12.3 property 与描述符入门

> 前置：7.2 继承与特殊方法 · 约 25 分钟 · 官方对应：[property](https://docs.python.org/zh-cn/3/library/functions.html#property)

## 目标

- 用 `@property` 把方法暴露成只读属性
- 知道描述符是 `@property` 的底层机制（了解即可）

## 核心概念

```python run
class User:
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        return self._name

u = User("Ada")
print(u.name)
```

## 易错点

- 对 property 加括号会 `TypeError`。
- setter 里忘记校验会导致脏数据。

## 对照

| | Python | JS | Java |
|---|---|---|---|
| 访问器 | `@property` | `get x()` | getter 方法 |

## 读代码

Pydantic/FastAPI 模型属性看似字段，底层可能是描述符或 dataclass 生成；读代码时仍按“属性访问”理解。

## 练习

```python exercise id=s12-l03-prop
# --- starter ---
class Box:
    def __init__(self, w):
        self._w = w
# --- solution ---
class Box:
    def __init__(self, w):
        self._w = w

    @property
    def w(self):
        return self._w
# --- check ---
b = Box(3)
assert b.w == 3
```

## 小结

- property 延迟计算或封装
- 读属性时不加括号

## 延伸阅读

- [描述符 HOWTO](https://docs.python.org/zh-cn/3/howto/descriptor.html)
