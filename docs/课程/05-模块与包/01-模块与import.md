---
title: 5.1 模块与 import
---

# 5.1 模块与 import

> 前置：3.2 · 约 30 分钟 · 官方对应：[模块](https://docs.python.org/zh-cn/3/tutorial/modules.html) · 核对日期 2026-10-06

## 目标

- 理解“模块就是一个 `.py` 文件”，模块本身是对象。
- 读懂 `import x`、`from x import y`、`import x as z`、`from x import y as z`。
- 知道 Python 按 `sys.path` 查找模块，模块只会执行一次。
- 理解 `if __name__ == "__main__":` 的作用。

## 核心概念

### 模块与四种 import 写法

一个 `.py` 文件就是一个**模块**，文件名（去掉 `.py`）即模块名。`import` 会执行该文件，并把得到的模块对象绑定到名字上。

| 写法 | 绑定的名字 | 使用方式 |
|---|---|---|
| `import os` | `os`（模块对象） | `os.getenv(...)` |
| `import os.path` | `os` | `os.path.join(...)` |
| `from os import getenv` | `getenv`（模块中的对象） | `getenv(...)` |
| `import numpy as np` | `np` | `np.array(...)` |
| `from os import getenv as env` | `env` | `env(...)` |

```python run
import math
from json import dumps
import datetime as dt

print(math.sqrt(16))
print(dumps({"ok": True}))
print(dt.date(2026, 10, 6).isoformat())
print(type(math), math.__name__)     # 模块是对象
print(dir(math)[:5])                 # 列出模块中的名字
```

### 自己写一个模块

下面的示例在临时目录里创建 `weather_tools.py`，再导入它（浏览器和本地都可运行）：

```python run
import importlib
from pathlib import Path

Path("weather_tools.py").write_text('''
"""天气工具模块。"""
DEFAULT_UNIT = "C"

def get_weather(city):
    return f"{city}：晴，22°{DEFAULT_UNIT}"

print(f"模块 {__name__} 被执行了")
''', encoding="utf-8")
importlib.invalidate_caches()        # 运行中新建的文件，需让导入系统刷新缓存

import weather_tools                 # 第一次导入：执行模块代码
import weather_tools                 # 再次导入：直接用缓存，不会再打印
from weather_tools import get_weather, DEFAULT_UNIT

print(weather_tools.get_weather("上海"), get_weather("北京"), DEFAULT_UNIT)
```

### 模块搜索路径

`import x` 时，Python 依次在 `sys.path` 的目录中查找 `x.py` 或包目录 `x/`。`sys.path` 大致由以下部分组成：

1. 被运行脚本所在目录（或交互模式下的当前目录）；
2. 环境变量 `PYTHONPATH`；
3. 标准库目录；
4. `site-packages`（第三方包安装位置；`uv run` 时是 `.venv/lib/python3.12/site-packages`）。

```python run
import sys
import json

print(sys.path[:3])
print(json.__file__)          # 模块文件位置：判断“这个名字从哪来”的利器
print("json" in sys.modules)  # 已导入模块的缓存
```

### `if __name__ == "__main__":`

每个模块都有 `__name__`：**被直接运行时是 `"__main__"`，被导入时是模块名**。把“只有直接运行时才执行”的代码放进这个判断，模块就既能被导入复用、又能当脚本运行。

```python run
import importlib
import runpy
from pathlib import Path

Path("greet.py").write_text('''
def greet(name):
    return f"你好，{name}"

if __name__ == "__main__":
    print("直接运行：", greet("脚本"))
''', encoding="utf-8")
importlib.invalidate_caches()

import greet                                   # 被导入：__name__ == "greet"，不执行 main 块
print("导入后：", greet.greet("模块"), greet.__name__)
runpy.run_path("greet.py", run_name="__main__")   # 模拟 python greet.py
```

## 易错点

- **文件名与标准库/第三方包同名**：把自己的文件命名为 `json.py`、`random.py`、`anthropic.py`，会遮蔽真正的模块，出现莫名其妙的 `AttributeError`。Python 3.13 起错误信息会提示“可能遮蔽了标准库模块”（核对日期 2026-10-06）。
- **`from x import *`**：把大量名字倒进当前命名空间，读码时无法判断名字来源；避免使用。
- **修改模块后在 REPL 中重新 `import` 没生效**：模块有缓存；重启解释器或用 `importlib.reload`。
- **`ModuleNotFoundError`**：先确认是否在项目环境中运行（`uv run`），再确认包名与导入名（见 1.2）。
- **`ImportError: cannot import name`**：模块存在，但里面没有这个名字（拼写错误、版本不同或循环导入）。

```python run raises=ImportError
from json import dump_string   # json 模块中没有这个名字
```

## 对照

| 写法 | Python | JS（ESM） | Java |
|---|---|---|---|
| 导入整个模块 | `import os` | `import * as os from "os"` | — |
| 导入具名对象 | `from os import getenv` | `import { getenv } from "os"` | `import java.util.List;` |
| 别名 | `import numpy as np` | `import { a as b }` | 无 |
| 模块单位 | 文件 | 文件 | 类（包是目录） |
| 导出控制 | 默认全部公开，`_` 前缀表示内部，`__all__` 控制 `*` | `export` 显式导出 | `public` / 包私有 |
| 入口判断 | `if __name__ == "__main__"` | `import.meta.main`（部分运行时） | `public static void main` |

## 读代码

```python
import os

import anthropic
from dotenv import load_dotenv
```

| 名字 | 来源 | 判断依据 |
|---|---|---|
| `os` | 标准库 | 在 [标准库索引](https://docs.python.org/zh-cn/3/library/index.html) 中 |
| `anthropic` | 第三方包 `anthropic` | `pyproject.toml` 依赖；`anthropic.__file__` 位于 `.venv/.../site-packages` |
| `load_dotenv` | 第三方包 `python-dotenv` 的 `dotenv` 模块 | 同上 |
| `print`、`range` | 内置 | 无需导入，见 [内置函数](https://docs.python.org/zh-cn/3/library/functions.html) |

`minimal_agent.py` 没有 `if __name__ == "__main__":`，所有代码都在模块顶层：它只作为脚本运行，不打算被导入（被导入时会立即发起 API 请求）。可复用的模块应把执行逻辑放进 `main()` 并用该判断保护。

## 练习

### 练习 1：判断来源

`SOURCES` 字典记录名字的来源，取值为 `"builtin"`、`"stdlib"`、`"third_party"` 之一。补全剩余条目。

```python exercise id=s05-l01-sources
# --- starter ---
SOURCES = {
    "print": "builtin",
    "os": None,
    "anthropic": None,
    "load_dotenv": None,
    "len": None,
    "json": None,
}
# --- solution ---
SOURCES = {
    "print": "builtin",
    "os": "stdlib",
    "anthropic": "third_party",
    "load_dotenv": "third_party",
    "len": "builtin",
    "json": "stdlib",
}
# --- check ---
expected = {"print": "builtin", "os": "stdlib", "anthropic": "third_party", "load_dotenv": "third_party", "len": "builtin", "json": "stdlib"}
for k, v in expected.items():
    assert SOURCES.get(k) == v, f"{k} 的来源应为 {v}"
```

### 练习 2：可导入也可运行

在 `mytool.py` 的源码字符串 `SOURCE` 中补上 `if __name__ == "__main__":` 判断，使它被导入时**不**打印 `"运行 main"`，直接运行时才打印。检查会分别导入和运行它。

```python exercise id=s05-l01-main-guard
# --- starter ---
SOURCE = '''
def add(a, b):
    return a + b

print("运行 main")
'''
# --- solution ---
SOURCE = '''
def add(a, b):
    return a + b

if __name__ == "__main__":
    print("运行 main")
'''
# --- check ---
import contextlib, importlib, io, runpy, sys
from pathlib import Path
Path("mytool.py").write_text(SOURCE, encoding="utf-8")
importlib.invalidate_caches()
sys.modules.pop("mytool", None)
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    import mytool
assert mytool.add(1, 2) == 3
assert "运行 main" not in buf.getvalue(), "被导入时不应打印"
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    runpy.run_path("mytool.py", run_name="__main__")
assert "运行 main" in buf.getvalue(), "直接运行时应打印"
```

## 小结

- 模块 = 文件，import 执行一次后缓存在 `sys.modules`。
- `import x` 用 `x.名字` 访问；`from x import y` 直接用 `y`。
- 模块按 `sys.path` 查找；`模块.__file__` 告诉你它在哪里。
- `__name__ == "__main__"` 区分“直接运行”与“被导入”。

## 延伸阅读

- [模块（教程）](https://docs.python.org/zh-cn/3/tutorial/modules.html)
- [模块搜索路径](https://docs.python.org/zh-cn/3/tutorial/modules.html#the-module-search-path)
- [`__main__` —— 顶层代码环境](https://docs.python.org/zh-cn/3/library/__main__.html)
- [导入系统（参考）](https://docs.python.org/zh-cn/3/reference/import.html)
