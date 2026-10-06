---
title: 6.1 读懂 Traceback
---

# 6.1 读懂 Traceback

> 前置：3.2 · 约 25 分钟 · 官方对应：[错误和异常](https://docs.python.org/zh-cn/3/tutorial/errors.html)、[内置异常](https://docs.python.org/zh-cn/3/library/exceptions.html) · 核对日期 2026-10-06

## 目标

- 按正确顺序阅读 Traceback：**先看最后一行，再从下往上找自己的代码**。
- 认识 10 种最常见的异常及其典型原因。
- 区分语法错误（运行前）与运行时异常。

## 核心概念

### Traceback 的结构

运行下面的代码，观察输出：

```python run raises=KeyError
PROVIDERS = {"deepseek": {"model": "deepseek-flash"}}

def load_config(provider):
    return PROVIDERS[provider]

def main():
    config = load_config("openai")
    print(config)

main()
```

典型 Traceback 由三部分组成：

```text
Traceback (most recent call last):          ← 标题：最近的调用在最后
  File "main.py", line 10, in <module>      ← 调用栈：从最外层（模块顶层）开始
    main()
  File "main.py", line 7, in main
    config = load_config("openai")
  File "main.py", line 4, in load_config    ← 最内层：真正出错的位置
    return PROVIDERS[provider]
           ~~~~~~~~~^^^^^^^^^^              ← 3.11 起：精确标出出错的子表达式
KeyError: 'openai'                          ← 最后一行：异常类型 + 信息
```

阅读顺序：

1. **最后一行**：异常类型（`KeyError`）和信息（缺的键是 `'openai'`）。
2. **往上一帧**：出错的文件、行号、函数和源码行。
3. **继续往上**：找到第一处**你自己的代码**（第三方库的帧可以先跳过），那里通常是根因——例如传错了参数。

### 常见异常速查

| 异常 | 典型原因 | 例子 |
|---|---|---|
| `NameError` | 名字未定义（拼写错误、忘记导入） | `prnt("x")` |
| `TypeError` | 类型不对或参数个数/名字不对 | `"1" + 1`、`f(**{"x": 1})` |
| `ValueError` | 类型对但值不合法 | `int("abc")` |
| `KeyError` | dict 中没有这个键 | `d["missing"]` |
| `IndexError` | 序列下标越界 | `[][0]` |
| `AttributeError` | 对象没有这个属性/方法 | `None.text`、`"s".append` |
| `ZeroDivisionError` | 除以零 | `1 / 0` |
| `FileNotFoundError` | 文件不存在 | `open("nope.txt")` |
| `ModuleNotFoundError` | 找不到模块 | `import anthropicc` |
| `SyntaxError` / `IndentationError` | 代码无法解析，**一行都不会执行** | 缺冒号、缩进错 |

```python run
cases = [
    lambda: int("abc"),
    lambda: [][0],
    lambda: None.text,
    lambda: {"a": 1}["b"],
    lambda: 1 / 0,
]
for f in cases:
    try:
        f()
    except Exception as e:          # 捕获后打印类型与信息（6.2 详解）
        print(f"{type(e).__name__}: {e}")
```

### 更友好的错误信息

近几个版本的 CPython 持续改进错误信息（核对日期 2026-10-06）：

- 3.10：`SyntaxError` 能指出未闭合的括号等更准确的位置；`NameError`/`AttributeError` 给出 “Did you mean …?” 建议。
- 3.11：Traceback 用 `~~~^^^` 标出具体出错的子表达式（[PEP 657](https://peps.python.org/pep-0657/)）。
- 3.12：遗漏导入标准库时提示 “Did you forget to import 'sys'?”。
- 3.13：Traceback 默认彩色；关键字参数拼错时提示正确的参数名。

```python run raises=AttributeError
class Block:
    def __init__(self):
        self.text = "你好"

b = Block()
print(b.txt)          # 信息中会出现 Did you mean: 'text'?
```

### 语法错误 vs 运行时异常

`SyntaxError` 在**编译阶段**发现，整个文件一行都不会执行；运行时异常则在执行到那一行时才抛出，之前的代码已经执行过了。

```python run raises=SyntaxError
print("这一行也不会执行")
if True
    print("缺少冒号")
```

## 易错点

- **从上往下读 Traceback**：最上面是最外层调用，最有用的信息在最后。
- **只看最后一行就去改第三方库**：库里的出错行通常只是“症状”，根因多半在你传入的参数，往上找你自己的代码帧。
- **`AttributeError: 'NoneType' object has no attribute …`**：说明某个变量意外为 `None`——往前找它的赋值来源（常见：函数漏写 `return`、`dict.get` 没取到值）。
- **异常信息里的 `During handling of the above exception, another exception occurred`**：表示处理异常时又出了新异常，两个都要看（6.2 讲异常链）。

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 调用栈名称 | Traceback | stack trace | stack trace |
| 栈的顺序 | 最近调用在**最后** | 最近调用在**最前** | 最近调用在**最前** |
| 缺键 | 抛 `KeyError` | 返回 `undefined` | `get` 返回 `null` |
| 访问 null 属性 | `AttributeError: 'NoneType' …` | `TypeError: Cannot read properties of null` | `NullPointerException` |

注意栈的顺序与 JS/Java **相反**：Python 把出错位置放在最下面。

## 读代码

把 `.env` 中的 `LLM_PROVIDER` 改成 `foo` 后运行 `minimal_agent.py`，会得到：

```text
Traceback (most recent call last):
  File ".../examples/agent/minimal_agent.py", line 35, in <module>
    config = PROVIDERS[provider]
             ~~~~~~~~~^^^^^^^^^^
KeyError: 'foo'
```

只有一帧（`<module>` 表示模块顶层代码），第 35 行用 `foo` 作键查 `PROVIDERS` 失败。再往上看第 34 行就能找到 `provider` 的来源：`os.getenv("LLM_PROVIDER")`。

## 练习

### 练习 1：解析 Traceback 最后一行

实现 `parse_error(tb_text)`：从 Traceback 文本中取出**最后一个非空行**，按第一个 `": "` 拆为 `(异常类型, 信息)`；没有 `": "` 时信息为 `""`。

```python exercise id=s06-l01-parse
# --- starter ---
def parse_error(tb_text):
    first = tb_text.strip().splitlines()[0]
    return first, ""
# --- solution ---
def parse_error(tb_text):
    last = [line for line in tb_text.splitlines() if line.strip()][-1].strip()
    kind, _, message = last.partition(": ")
    return kind, message
# --- check ---
tb = """Traceback (most recent call last):
  File "main.py", line 4, in load_config
    return PROVIDERS[provider]
KeyError: 'openai'
"""
assert parse_error(tb) == ("KeyError", "'openai'"), parse_error(tb)
assert parse_error("Traceback...\nValueError: invalid literal for int() with base 10: 'abc'\n\n") == (
    "ValueError",
    "invalid literal for int() with base 10: 'abc'",
)
assert parse_error("Traceback...\nKeyboardInterrupt") == ("KeyboardInterrupt", "")
```

### 练习 2：预测异常类型

不运行代码，写出每个表达式会抛出的异常类型名（字符串）。检查会真正执行并比对。

```python exercise id=s06-l01-predict
# --- starter ---
PREDICTIONS = {
    'int("3.5")': "",
    '{"a": 1}["A"]': "",
    '"abc".push("d")': "",
    '[1, 2, 3][3]': "",
    'len(5)': "",
}
# --- solution ---
PREDICTIONS = {
    'int("3.5")': "ValueError",
    '{"a": 1}["A"]': "KeyError",
    '"abc".push("d")': "AttributeError",
    '[1, 2, 3][3]': "IndexError",
    'len(5)': "TypeError",
}
# --- check ---
for expr, predicted in PREDICTIONS.items():
    try:
        eval(expr)
    except Exception as e:
        actual = type(e).__name__
    assert predicted == actual, f"{expr} 实际抛出 {actual}，你的预测是 {predicted!r}"
```

## 小结

- Traceback：最后一行是结论（类型 + 信息），往上逐帧是调用路径，最近的调用在最下面。
- 根因通常在“你自己的代码”中最靠下的那一帧。
- 记住常见异常的典型原因；`'NoneType' object has no attribute` 意味着去找 `None` 的来源。

## 延伸阅读

- [错误和异常（教程）](https://docs.python.org/zh-cn/3/tutorial/errors.html)
- [内置异常与层次结构](https://docs.python.org/zh-cn/3/library/exceptions.html#exception-hierarchy)
- [traceback 模块](https://docs.python.org/zh-cn/3/library/traceback.html)
- [PEP 657：Traceback 中的细粒度错误位置](https://peps.python.org/pep-0657/)
