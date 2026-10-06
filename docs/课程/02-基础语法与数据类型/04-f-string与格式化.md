---
title: 2.4 f-string 与格式化
---

# 2.4 f-string 与格式化

> 前置：2.3 · 约 20 分钟 · 官方对应：[格式化字符串字面值](https://docs.python.org/zh-cn/3/tutorial/inputoutput.html#formatted-string-literals)、[格式规格迷你语言](https://docs.python.org/zh-cn/3/library/string.html#format-specification-mini-language) · 核对日期 2026-10-06

## 目标

- 用 f-string 把表达式嵌入字符串，并用格式说明符控制宽度、精度、对齐。
- 掌握 `f"{x=}"` 调试写法与 `!r` 转换。
- 能读懂旧式的 `str.format()` 与 `%` 格式化。

## 核心概念

### f-string 基础

以 `f` 或 `F` 为前缀的字符串中，`{}` 内是**任意表达式**，运行时求值后转为字符串插入：

```python run
city, temp = "上海", 22
print(f"{city}：晴，{temp}°C")
print(f"明天 {temp + 1}°C，城市名长度 {len(city)}")
turn = 2
print(f"[第 {turn} 轮] 调用工具")
print(f"字面量花括号要写两次：{{}}")
```

### 格式说明符

`{值:格式}`，冒号后是格式规格：

| 格式 | 含义 | 例子 → 结果 |
|---|---|---|
| `.2f` | 保留 2 位小数 | `f"{3.14159:.2f}"` → `'3.14'` |
| `,` | 千分位 | `f"{1234567:,}"` → `'1,234,567'` |
| `.1%` | 百分比 | `f"{0.256:.1%}"` → `'25.6%'` |
| `>8` / `<8` / `^8` | 右/左/居中对齐，宽度 8 | `f"{'ok':>8}"` → `'      ok'` |
| `08.3f` | 用 0 填充到宽度 8 | `f"{3.5:08.3f}"` → `'0003.500'` |
| `x` / `b` | 十六进制 / 二进制 | `f"{255:x}"` → `'ff'` |

```python run
rows = [("deepseek", 0.8123, 1200), ("anthropic", 0.95, 35000)]
for name, score, tokens in rows:
    print(f"{name:<10}|{score:>7.1%}|{tokens:>8,}")

width = 12
print(f"{'动态宽度':>{width}}")   # 格式规格中也可以嵌套 {}
```

### 调试写法与转换

- `f"{expr=}"`（3.8 起）：输出“表达式=值”，适合临时打印调试。
- `!r` 用 `repr()` 转换（字符串会带引号，便于看清空白）；`!s` 用 `str()`。

```python run
provider = "deepseek "
max_turns = 5
print(f"{provider=}")       # provider='deepseek '
print(f"{max_turns * 2 = }")  # 等号两侧空格会保留
print(f"{provider!r} vs {provider}")
```

### 3.12 起的写法放宽

[PEP 701](https://peps.python.org/pep-0701/)（Python 3.12）把 f-string 纳入正式语法：`{}` 内可以复用外层同类引号、可以跨行、可以包含反斜杠。本项目固定 3.12，可以使用；但如果代码需要兼容 3.11 及以下就不能这样写。

```python run
config = {"model": "deepseek-flash"}
print(f"模型：{config["model"]}")   # 3.12 起：内部可用同类引号
print(f"模型：{config['model']}")   # 兼容所有版本的写法
```

3.14 新增的模板字符串（t-string，[PEP 750](https://peps.python.org/pep-0750/)）写法类似但前缀为 `t`，结果不是 `str` 而是 `Template` 对象，供库做安全的插值处理（如 SQL、HTML）。读到时知道它不是 f-string 即可：

```python fragment
from string.templatelib import Template
greeting: Template = t"Hello {name}"  # 仅 3.14+
```

### 旧式格式化的读法

```python run
name, n = "Python", 3
print("{} 有 {} 个版本".format(name, n))          # str.format
print("{0}-{0}-{1}".format("a", "b"))             # 按位置复用
print("%s 有 %d 个版本，%.1f" % (name, n, 3.14))  # % 格式化（C 风格，老代码常见）
```

## 易错点

- **忘了 `f` 前缀**：`"{city}"` 会原样输出花括号。
- **f-string 不能延迟求值**：写下的瞬间就求值。日志中推荐 `logger.info("用户 %s", name)` 而不是 f-string（见 8.6）。
- **格式说明符与类型不匹配**：例如对字符串用 `:.2f`，抛 `ValueError`。

```python run raises=ValueError
price = "9.9"
print(f"{price:.2f}")   # price 是 str，不能用浮点格式
```

## 对照

| 写法 | Python | JS | Java |
|---|---|---|---|
| 插值 | `f"Hi {name}"` | `` `Hi ${name}` `` | `"Hi %s".formatted(name)` / `String.format` |
| 保留两位 | `f"{x:.2f}"` | `x.toFixed(2)` | `String.format("%.2f", x)` |
| 千分位 | `f"{n:,}"` | `n.toLocaleString()` | `String.format("%,d", n)` |
| 调试打印 | `f"{x=}"` | 无 | 无 |

## 读代码

```python
def get_weather(city):
    return f"{city}：晴，22°C"

print(f"[配置] provider={provider} model={model}")
print(f"[第 {turn} 轮] 调用工具 {block.name}({block.input}) -> {output}")
```

最后一行中 `{block.input}` 是一个 dict，f-string 对它调用 `str()`，因此输出 `{'city': '上海'}`（Python 的 dict 字面量形式，不是 JSON）。需要 JSON 时用 `json.dumps(block.input, ensure_ascii=False)`（见 8.2）。

## 练习

### 练习 1：格式化报表行

实现 `report_line(name, score, tokens)`：名字左对齐宽 10，分数为百分比保留 1 位、右对齐宽 7，tokens 带千分位、右对齐宽 8，三段用 `|` 连接。

```python exercise id=s02-l04-report
# --- starter ---
def report_line(name, score, tokens):
    return f"{name}|{score}|{tokens}"
# --- solution ---
def report_line(name, score, tokens):
    return f"{name:<10}|{score:>7.1%}|{tokens:>8,}"
# --- check ---
assert report_line("deepseek", 0.8123, 1200) == "deepseek  |  81.2%|   1,200", repr(report_line("deepseek", 0.8123, 1200))
assert report_line("x", 1, 35000) == "x         | 100.0%|  35,000", repr(report_line("x", 1, 35000))
```

### 练习 2：工具调用日志

实现 `log_line(turn, name, args, output)`，返回形如 `[第 1 轮] 调用工具 get_weather({'city': '上海'}) -> 上海：晴，22°C` 的字符串（与 `minimal_agent.py` 的打印格式一致）。

```python exercise id=s02-l04-log
# --- starter ---
def log_line(turn, name, args, output):
    ...
# --- solution ---
def log_line(turn, name, args, output):
    return f"[第 {turn} 轮] 调用工具 {name}({args}) -> {output}"
# --- check ---
got = log_line(1, "get_weather", {"city": "上海"}, "上海：晴，22°C")
assert got == "[第 1 轮] 调用工具 get_weather({'city': '上海'}) -> 上海：晴，22°C", got
```

## 小结

- f-string 的 `{}` 内是表达式，`:` 后是格式规格。
- `f"{x=}"` 调试、`!r` 看清值的真实形态。
- 3.12 起 f-string 内可复用同类引号；`.format()` 与 `%` 是旧写法，读懂即可。

## 延伸阅读

- [格式化字符串字面值（教程）](https://docs.python.org/zh-cn/3/tutorial/inputoutput.html#formatted-string-literals)
- [f-string 语法参考](https://docs.python.org/zh-cn/3/reference/lexical_analysis.html#f-strings)
- [格式规格迷你语言](https://docs.python.org/zh-cn/3/library/string.html#format-specification-mini-language)
- [PEP 701：f-string 语法形式化](https://peps.python.org/pep-0701/)
- [PEP 750：模板字符串](https://peps.python.org/pep-0750/)
