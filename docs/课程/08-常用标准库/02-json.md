---
title: 8.2 json
---

# 8.2 json

> 前置：4.2 · 约 20 分钟 · 官方对应：[使用 json 保存结构化数据](https://docs.python.org/zh-cn/3/tutorial/inputoutput.html#saving-structured-data-with-json)、[json 模块](https://docs.python.org/zh-cn/3/library/json.html)

## 目标

- 掌握 `json.dumps` / `json.loads`（字符串）与 `json.dump` / `json.load`（文件）。
- 知道 JSON 与 Python 类型的对应关系及其不对称之处。
- 用 `ensure_ascii=False`、`indent` 输出可读的中文 JSON；处理解析错误。

## 核心概念

### 字符串 ⇄ 对象

```python run
import json

blocks = [{"type": "text", "text": "你好"}, {"type": "tool_use", "name": "get_weather", "input": {"city": "上海"}}]

s = json.dumps(blocks)                                  # Python 对象 → JSON 字符串
print(s)                                                # 中文被转义为 \uXXXX
print(json.dumps(blocks, ensure_ascii=False))           # 保留中文
print(json.dumps(blocks[1], ensure_ascii=False, indent=2))   # 缩进美化

back = json.loads(s)                                    # JSON 字符串 → Python 对象
print(back == blocks, type(back), type(back[0]))
```

记忆：带 `s` 的是 **s**tring（`dumps`/`loads`），不带 `s` 的操作文件对象（`dump`/`load`）。

### 文件读写

```python run
import json
from pathlib import Path

data = {"provider": "deepseek", "max_turns": 5, "tools": ["get_weather"]}
with open("config.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

with open("config.json", encoding="utf-8") as f:
    loaded = json.load(f)
print(loaded)
print(Path("config.json").read_text(encoding="utf-8"))
```

### 类型对应

| JSON | Python（`loads` 得到） | Python → JSON（`dumps`） |
|---|---|---|
| object `{}` | `dict` | `dict` → object |
| array `[]` | `list` | `list`、`tuple` → array |
| string | `str` | `str` |
| number | `int` / `float` | `int`、`float` |
| `true` / `false` | `True` / `False` | |
| `null` | `None` | |

不对称之处：

```python run
import json

print(json.loads(json.dumps((1, 2))))          # tuple → list，回不来
print(json.dumps({1: "a"}))                    # 非字符串键会被转成字符串
print(json.loads(json.dumps({1: "a"})))        # {'1': 'a'}
print(json.dumps({"ok": True, "v": None}))     # true / null
```

### 序列化自定义对象

`set`、`datetime`、自定义类默认无法序列化，用 `default=` 提供转换函数：

```python run
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

@dataclass
class Call:
    name: str
    at: datetime

def to_jsonable(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, set):
        return sorted(obj)
    raise TypeError(f"无法序列化 {type(obj).__name__}")

call = Call("get_weather", datetime(2026, 10, 6, 8, 0, tzinfo=timezone.utc))
print(json.dumps(asdict(call), default=to_jsonable))
print(json.dumps({"tags": {"b", "a"}}, default=to_jsonable))
```

## 易错点

- **把 `str(dict)` 当作 JSON**：`str({"a": None})` 是 `"{'a': None}"`（单引号、`None`），不是合法 JSON；用 `json.dumps`。
- **解析不合法的 JSON**：抛 `json.JSONDecodeError`（`ValueError` 的子类），信息里有行列号。模型输出的“JSON”尤其要防御。
- **中文变成 `\u4f60\u597d`**：不是乱码，是转义；加 `ensure_ascii=False`。
- **`dumps` 无法序列化的类型**：抛 `TypeError: Object of type … is not JSON serializable`。

```python run raises=JSONDecodeError
import json

json.loads("{'city': '上海'}")     # JSON 要求双引号
```

## 对照

| 操作 | Python | JS | Java（Jackson） |
|---|---|---|---|
| 对象 → 字符串 | `json.dumps(o)` | `JSON.stringify(o)` | `mapper.writeValueAsString(o)` |
| 字符串 → 对象 | `json.loads(s)` | `JSON.parse(s)` | `mapper.readValue(s, T.class)` |
| 美化 | `indent=2` | `JSON.stringify(o, null, 2)` | `writerWithDefaultPrettyPrinter()` |
| 自定义转换 | `default=` | `toJSON()` / replacer | 注解 / 序列化器 |

## 读代码

工具调用在协议层就是 JSON：`tools` 中的 `input_schema` 是 JSON Schema（一种描述 JSON 结构的规范）；模型返回的 `block.input` 是解析后的 dict（SDK 已经替你 `loads` 过了）。

```python
print(f"[第 {turn} 轮] 调用工具 {block.name}({block.input}) -> {output}")
# 输出：调用工具 get_weather({'city': '上海'}) -> ...   ← 这是 Python dict 的 str()，不是 JSON
```

若要把消息历史保存成文件以便调试，可以写：

```python
Path("messages.json").write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
```

注意 `resp.content` 中是 SDK 的模型对象，需先转换（`block.model_dump()`）才能 `json.dumps`。

## 练习

### 练习 1：安全解析模型输出

实现 `parse_args(text)`：把字符串解析为 dict 并返回；解析失败或结果不是 dict 时返回 `{}`。

```python exercise id=s08-l02-parse
# --- starter ---
import json

def parse_args(text):
    return json.loads(text)
# --- solution ---
import json

def parse_args(text):
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}
# --- check ---
assert parse_args('{"city": "上海"}') == {"city": "上海"}
assert parse_args("{'city': '上海'}") == {}, "单引号不是合法 JSON"
assert parse_args("[1, 2]") == {}, "不是对象时返回 {}"
assert parse_args("") == {}
```

### 练习 2：往返转换

实现 `pretty(obj)`：返回 `ensure_ascii=False`、`indent=2` 的 JSON 字符串；实现 `roundtrip_equal(obj)`：判断 `obj` 经过 `dumps` 再 `loads` 后是否与原对象相等。

```python exercise id=s08-l02-roundtrip
# --- starter ---
import json

def pretty(obj):
    return json.dumps(obj)

def roundtrip_equal(obj):
    return True
# --- solution ---
import json

def pretty(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2)

def roundtrip_equal(obj):
    return json.loads(json.dumps(obj)) == obj
# --- check ---
assert pretty({"城市": "上海"}) == '{\n  "城市": "上海"\n}', pretty({"城市": "上海"})
assert roundtrip_equal({"a": [1, 2], "b": None}) is True
assert roundtrip_equal({"t": (1, 2)}) is False, "tuple 会变成 list"
assert roundtrip_equal({1: "a"}) is False, "非字符串键会变成字符串"
```

## 小结

- `dumps`/`loads` 处理字符串，`dump`/`load` 处理文件。
- 中文用 `ensure_ascii=False`，美化用 `indent`。
- tuple→list、非字符串键→字符串，往返不完全对称。
- 解析外部输入要捕获 `json.JSONDecodeError`。

## 延伸阅读

- [使用 json 保存结构化数据（教程）](https://docs.python.org/zh-cn/3/tutorial/inputoutput.html#saving-structured-data-with-json)
- [json 模块](https://docs.python.org/zh-cn/3/library/json.html)
