---
title: 12.3 property 与描述符入门
---

# 12.3 property 与描述符入门

> 前置：7.2 继承与特殊方法、10.2 装饰器 · 约 35 分钟 · 官方对应：[property 内置函数](https://docs.python.org/zh-cn/3/library/functions.html#property)、[描述符 HOWTO](https://docs.python.org/zh-cn/3/howto/descriptor.html)

## 目标

- 用 `@property` 把方法暴露成**像字段一样的只读属性**，并在 setter 里做校验。
- 理解访问 `obj.attr` 时，解释器会查找描述符协议：`__get__` / `__set__` / `__delete__`。
- 知道 `@property` 本质是 `property(fget, fset, fdel)` 返回的描述符对象。
- 区分“公有属性名”与“内部存储 `_name`”的封装习惯，避免在 setter 里递归赋值。

## 核心概念

### `@property`：只读访问器

对外 `user.name`，对内用 `_name` 存储，避免调用方加括号。

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

`property` 装饰器把 `name` 方法替换成描述符实例；读取 `u.name` 时不会把 `name` 当普通函数绑定。

### getter / setter / deleter

需要写入时，用**同名**方法加 `@name.setter`；删除用 `@name.deleter`。

```python run
class Celsius:
    def __init__(self, c: float) -> None:
        self._c = c

    @property
    def c(self) -> float:
        return self._c

    @c.setter
    def c(self, value: float) -> None:
        if value < -273.15:
            raise ValueError("低于绝对零度")
        self._c = float(value)

    @property
    def f(self) -> float:
        return self._c * 9 / 5 + 32

box = Celsius(25)
box.c = 30
print(box.c, round(box.f, 1))
```

只读属性不要定义 setter；写操作集中在 setter 里，便于统一校验与日志。

### 描述符协议（`property` 的底层）

描述符是定义了 `__get__`、`__set__` 或 `__delete__` 的**类属性**。访问 `instance.attr` 时，若 `type(instance).__dict__['attr']` 是描述符，则调用描述符方法，而不是直接读实例 `__dict__`。

```python run
class Verbose:
    def __init__(self, label: str) -> None:
        self.label = label

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return f"{self.label}={obj.__dict__.get(self.label, '?')}"

    def __set__(self, obj, value):
        obj.__dict__[self.label] = value

class Bag:
    x = Verbose("x")

b = Bag()
b.x = 10
print(b.x)
```

`@property` 是标准库帮你写好的描述符；除非你在写框架，多数业务代码用 `@property` 足够。

### 与特殊方法、数据模型的关系

`property` 不参与 `__eq__` 或 `__repr__` 的自动合成；`dataclass` 生成的字段也不是简单的 `@property`，但**读代码时**仍按属性访问理解。核对日期 2026-10-18：描述符行为在 Python 3.12（项目版本）与 3.15 稳定版一致，详见 [数据模型 · 描述符](https://docs.python.org/zh-cn/3/reference/datamodel.html#descriptors)。

```python run
class Rect:
    def __init__(self, w: float, h: float) -> None:
        self._w, self._h = w, h

    @property
    def area(self) -> float:
        return self._w * self._h

    def __repr__(self) -> str:
        return f"Rect(w={self._w}, h={self._h}, area={self.area})"

r = Rect(3, 4)
print(r)
```


## 易错点

- **对 property 加括号**：`u.name()` 会 `TypeError`，因为 `name` 已不是函数。
- **setter 里写 `self.name = value`**：会再次触发 setter，导致无限递归；应写入 `self._name` 等内部字段。
- **在 `__init__` 里绕过 setter**：若 `__init__` 直接 `self._c = c` 而 setter 有校验，要清楚哪条路径负责校验；常见写法是 `__init__` 也走 setter 或调用私有校验函数。
- **类属性描述符与实例属性同名覆盖**：在实例 `__dict__` 里直接赋同名键会遮蔽描述符（除非描述符只在类上）；读复杂类时注意属性定义在类上还是实例上。

```python run raises=TypeError
class U:
    @property
    def name(self):
        return "x"

U().name()
```

```python run raises=ValueError
class T:
    @property
    def n(self):
        return self._n

    @n.setter
    def n(self, v):
        if v < 0:
            raise ValueError("n 必须非负")
        self._n = v

t = T()
t.n = -1
```

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 只读访问 | `@property` | `get width()` | `getWidth()` 或 `record` 访问器 |
| 可写访问 | `@x.setter` | `set width(v)` | `setWidth(v)` |
| 底层机制 | 描述符 `__get__`/`__set__` | 属性描述符 `Object.defineProperty` | 字节码 + 访问器方法 |
| 装饰器语法 | `@property` 是装饰器 | 类字段提案 | 无直接等价，靠 IDE 生成 |

## 读代码

`ring_buffer.py` 用公有方法 `append` 管理写入，用 dunder 暴露只读视图；若要把“逻辑长度”做成只读属性，典型写法是：

```python fragment
    def __len__(self) -> int:
        return self._size

    def __repr__(self) -> str:
        return f"RingBuffer({list(self)!r}, cap={self._cap})"
```

- 第 1–2 行：`__len__` 等价于只读的 `size` 属性，调用方写 `len(buf)` 而不是 `buf.size()`。
- 第 4–5 行：`__repr__` 里 `list(self)` 依赖 `__iter__`，展示的是**逻辑顺序**的元素列表，而不是底层 `_data` 的物理排列。
- 读代码时看到 `list(self)` 在 `__repr__` 里，要想到迭代协议与属性访问是两条不同路径，但都可以用来构造调试字符串。
- 若改为 `@property def size(self): return self._size`，语义与 `__len__` 类似，但 `len()` 内置不会自动调用 `size` 属性。
- 封装 `_size`、`_start` 避免外部直接改指针，与 `@property` 保护不变式的目标一致。
- `append` 方法集中修改 `_size` 与 `_start`，是命令式 API；property 更适合**派生量**（如 `area`、`f`）。
- 描述符常用于 ORM / 验证库：赋值时运行校验，比在每个方法里重复 `if` 更集中。
- Pydantic v2 字段在运行时由模型内部机制处理，静态上像属性，实现不必手写 `@property`，但调试时仍按属性读。
- FastAPI 依赖注入参数是普通函数参数，不要和实例 property 混淆。
- 读 `minimal_agent.py` 时，`config["model"]` 是 dict 下标，不是 property；对比 SDK 对象上可能的 `@cached_property`（见 10.2）。
- 工具函数 `get_weather` 是普通 def，没有 property；只有当你把“延迟加载的配置”挂在对象上时才需要访问器。

## 练习

### 练习 1：只读 `w`

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

### 练习 2：带校验的 setter（5 行以上逻辑）

`Percent` 存储 0–100 的浮点数；属性名 `value`，赋值越界抛 `ValueError`。

```python exercise id=s12-l03-percent
# --- starter ---
class Percent:
    def __init__(self, value: float) -> None:
        self._value = 0.0
# --- solution ---
class Percent:
    def __init__(self, value: float) -> None:
        self.value = value

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, v: float) -> None:
        x = float(v)
        if x < 0.0 or x > 100.0:
            raise ValueError("percent 必须在 0..100")
        self._value = x
# --- check ---
p = Percent(50)
assert p.value == 50
p.value = 0
p.value = 100
try:
    p.value = 100.1
    raise AssertionError("应抛出 ValueError")
except ValueError:
    pass
```

## 小结

- `@property` 提供只读属性；`@x.setter` 集中校验与赋值。
- 描述符是 `property` 的底层；访问 `obj.attr` 可能走 `__get__` 而不是实例字典。
- setter 写入 `_field`，不要 `self.attr = ...` 递归。
- 读容器 / SDK：区分 dict 下标、普通方法、property 与 dunder 四种访问方式。

## 延伸阅读

- [内置函数 property](https://docs.python.org/zh-cn/3/library/functions.html#property)
- [描述符 HOWTO](https://docs.python.org/zh-cn/3/howto/descriptor.html)
- [数据模型 · 描述符](https://docs.python.org/zh-cn/3/reference/datamodel.html#descriptors)
