---
title: 8.5 collections 与 itertools
---

# 8.5 collections 与 itertools

> 前置：4.4 · 约 25 分钟 · 官方对应：[collections](https://docs.python.org/zh-cn/3/library/collections.html)、[itertools](https://docs.python.org/zh-cn/3/library/itertools.html) · 核对日期 2026-10-06

## 目标

- 认识 `Counter`、`defaultdict`、`deque`、`namedtuple` 的典型用途。
- 认识 `itertools` 中最常见的几个函数：`chain`、`islice`、`groupby`、`batched`、`product`。
- 读码时一眼看出它们替代了哪段手写逻辑。

## 核心概念

### Counter：计数

```python run
from collections import Counter

types = ["text", "tool_use", "text", "thinking", "tool_use", "text"]
c = Counter(types)
print(c)                       # Counter({'text': 3, 'tool_use': 2, 'thinking': 1})
print(c["text"], c["missing"]) # 缺失的键计为 0，不抛 KeyError
print(c.most_common(2))
c.update(["text"])
print(c["text"])
```

### defaultdict：缺键时自动创建默认值

```python run
from collections import defaultdict

calls = [("get_weather", "上海"), ("get_time", "上海"), ("get_weather", "北京")]
by_tool = defaultdict(list)            # 缺键时调用 list() 创建空列表
for name, city in calls:
    by_tool[name].append(city)
print(dict(by_tool))

counts = defaultdict(int)              # int() == 0
for name, _ in calls:
    counts[name] += 1
print(dict(counts))
```

### deque：双端队列

两端追加、弹出都是 O(1)；`maxlen` 让它自动丢弃最旧的元素，适合“只保留最近 N 条”：

```python run
from collections import deque

recent = deque(maxlen=3)
for i in range(1, 6):
    recent.append(f"消息{i}")
print(list(recent))            # ['消息3', '消息4', '消息5']

q = deque(["a", "b"])
q.appendleft("start")
print(q.popleft(), q.pop(), list(q))
```

### namedtuple：带字段名的元组

```python run
from collections import namedtuple

Usage = namedtuple("Usage", ["input_tokens", "output_tokens"])
u = Usage(120, 45)
print(u.input_tokens, u[1], u)          # 既能按名字也能按下标访问
total = sum(u)
print(total, u._asdict())
```

新代码中更常见的是 `typing.NamedTuple` 或 `@dataclass`（7.3），读老代码时会遇到 `namedtuple`。

### itertools 常用函数

```python run
from itertools import chain, islice, groupby, product, batched

print(list(chain([1, 2], (3,), "ab")))                  # 串联多个可迭代对象
print(list(islice(range(100), 2, 10, 3)))                # 对任意迭代器切片
print(list(batched(range(7), 3)))                        # 3.12 起：按大小分批
print(list(product(["上海", "北京"], ["晴", "雨"])))      # 笛卡尔积

blocks = [{"type": "text"}, {"type": "text"}, {"type": "tool_use"}, {"type": "text"}]
for key, group in groupby(blocks, key=lambda b: b["type"]):   # 只合并“相邻”的相同键
    print(key, len(list(group)))
```

## 易错点

- **`groupby` 只合并相邻元素**：要按键全局分组，先 `sorted(..., key=同一个函数)`，或用 `defaultdict(list)`。
- **`defaultdict` 读取也会插入**：`d["x"]` 即使只是读取，也会创建键 `"x"`；只读判断用 `"x" in d` 或 `d.get("x")`。
- **`itertools.batched` 需要 3.12+**：本项目固定 3.12 可用；更低版本需自行实现。
- **迭代器只能消费一次**：`groupby` 的每个 `group` 必须在进入下一组之前用完。

```python run
from collections import defaultdict

d = defaultdict(list)
print("x" in d)
_ = d["x"]            # 读取也会创建
print("x" in d, dict(d))
```

## 对照

| 需求 | Python | JS | Java |
|---|---|---|---|
| 计数 | `Counter(xs)` | `Map` + 循环 / `Object.groupBy` 后计数 | `Collectors.groupingBy(…, counting())` |
| 分组 | `defaultdict(list)` | `Object.groupBy(xs, f)` | `Collectors.groupingBy(f)` |
| 双端队列 | `deque` | 数组（`unshift` 为 O(n)） | `ArrayDeque` |
| 分批 | `itertools.batched` | 手写 | 手写 / Guava `Lists.partition` |

## 读代码

```python
from collections import Counter

usage = Counter()
for resp in responses:
    usage["input_tokens"] += resp.usage.input_tokens
    usage["output_tokens"] += resp.usage.output_tokens
```

```python
history = deque(maxlen=50)     # 只保留最近 50 条消息，自动淘汰旧的
```

看到这些容器时，先在脑中把它“展开”成等价的普通 dict/list 写法，就容易理解了。

## 练习

### 练习 1：统计工具调用

实现 `tool_stats(calls)`：`calls` 是工具名列表，返回出现次数最多的前两项 `[(名字, 次数), ...]`（次数相同按首次出现顺序）。使用 `Counter.most_common`。

```python exercise id=s08-l05-counter
# --- starter ---
from collections import Counter

def tool_stats(calls):
    return []
# --- solution ---
from collections import Counter

def tool_stats(calls):
    return Counter(calls).most_common(2)
# --- check ---
calls = ["get_weather", "get_time", "get_weather", "search", "get_time", "get_weather"]
assert tool_stats(calls) == [("get_weather", 3), ("get_time", 2)], tool_stats(calls)
assert tool_stats([]) == []
```

### 练习 2：按角色分组

实现 `group_by_role(messages)`：返回 `{角色: [content, ...]}` 的普通 dict，角色顺序按首次出现。使用 `defaultdict(list)`。

```python exercise id=s08-l05-group
# --- starter ---
from collections import defaultdict

def group_by_role(messages):
    groups = defaultdict(list)
    return groups
# --- solution ---
from collections import defaultdict

def group_by_role(messages):
    groups = defaultdict(list)
    for m in messages:
        groups[m["role"]].append(m["content"])
    return dict(groups)
# --- check ---
msgs = [
    {"role": "user", "content": "q1"},
    {"role": "assistant", "content": "a1"},
    {"role": "user", "content": "q2"},
]
got = group_by_role(msgs)
assert got == {"user": ["q1", "q2"], "assistant": ["a1"]}, got
assert type(got) is dict, "请返回普通 dict（dict(groups)）"
```

## 小结

- `Counter` 计数、`defaultdict` 自动默认值、`deque(maxlen=N)` 保留最近 N 条、`namedtuple` 具名元组。
- `itertools`：`chain` 串联、`islice` 切片、`batched` 分批（3.12+）、`groupby` 相邻分组。
- 读码时把它们展开成普通 dict/list 逻辑来理解。

## 延伸阅读

- [collections](https://docs.python.org/zh-cn/3/library/collections.html)
- [itertools](https://docs.python.org/zh-cn/3/library/itertools.html)
- [itertools.batched](https://docs.python.org/zh-cn/3/library/itertools.html#itertools.batched)
