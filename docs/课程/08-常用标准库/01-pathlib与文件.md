---
title: 8.1 pathlib 与文件
---

# 8.1 pathlib 与文件

> 前置：6.3 · 约 25 分钟 · 官方对应：[pathlib](https://docs.python.org/zh-cn/3/library/pathlib.html)、[读写文件](https://docs.python.org/zh-cn/3/tutorial/inputoutput.html#reading-and-writing-files)

## 目标

- 用 `pathlib.Path` 拼接、拆解、判断路径。
- 读写文本文件，始终显式指定 `encoding="utf-8"`。
- 遍历目录、按模式查找文件。
- 读懂 `Path(__file__).resolve().parent` 这类定位项目文件的写法。

## 核心概念

### Path 对象

```python run
from pathlib import Path

p = Path("examples") / "agent" / "minimal_agent.py"   # 用 / 拼接路径，跨平台
print(p)
print(p.name, p.stem, p.suffix)       # minimal_agent.py  minimal_agent  .py
print(p.parent, p.parent.name)        # examples/agent  agent
print(p.with_suffix(".md"))
print(p.parts)
print(Path.cwd().is_absolute(), p.is_absolute())
```

### 读写文件

`Path` 提供一行读写的便捷方法；需要逐行处理大文件时用 `open()`。

```python run
from pathlib import Path

out = Path("output") / "log.txt"
out.parent.mkdir(parents=True, exist_ok=True)       # 创建目录（含父目录，已存在不报错）
out.write_text("第一行\n第二行\n", encoding="utf-8")
print(out.exists(), out.is_file(), out.stat().st_size, "字节")
print(out.read_text(encoding="utf-8").splitlines())

with out.open("a", encoding="utf-8") as f:            # 追加模式
    f.write("第三行\n")
with out.open(encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        print(i, line.rstrip("\n"))
```

| 模式 | 含义 |
|---|---|
| `"r"`（默认） | 读，文件不存在抛 `FileNotFoundError` |
| `"w"` | 写，**清空**已有内容 |
| `"a"` | 追加 |
| `"x"` | 新建，文件已存在则报错 |
| `"rb"` / `"wb"` | 二进制读写（`bytes`），不指定编码 |

### 遍历与查找

```python run
from pathlib import Path

for name in ["a.py", "b.md", "pkg/c.py", "pkg/sub/d.py"]:
    f = Path("proj") / name
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text("# demo\n", encoding="utf-8")

root = Path("proj")
print(sorted(p.name for p in root.iterdir()))               # 当前层
print(sorted(str(p) for p in root.glob("*.py")))            # 当前层匹配
print(sorted(str(p) for p in root.rglob("*.py")))           # 递归匹配
```

### 定位与脚本同目录的文件

脚本中常见写法：以**脚本文件所在目录**为基准，而不是以当前工作目录为基准。

```python
from pathlib import Path

HERE = Path(__file__).resolve().parent          # 当前 .py 文件所在目录
PROJECT_ROOT = HERE.parent.parent               # 向上两级
config_path = PROJECT_ROOT / "pyproject.toml"
```

`__file__` 是当前模块的文件路径；`resolve()` 转为绝对路径并解析符号链接。`load_dotenv()` 不传路径时，也是从调用它的文件所在目录开始向上查找 `.env`。

## 易错点

- **不指定编码**：`open(path)` 的默认编码取决于系统区域设置（Windows 上常不是 UTF-8），中文可能乱码；始终写 `encoding="utf-8"`。
- **相对路径以“当前工作目录”为基准**，不是以脚本位置为基准：在不同目录运行同一个脚本，结果不同。
- **`"w"` 模式会清空文件**。
- **用字符串拼路径** `"dir" + "/" + name`：用 `Path` 的 `/`。

```python run raises=FileNotFoundError
from pathlib import Path

Path("config/settings.toml").read_text(encoding="utf-8")
```

## 对照

| 操作 | Python | Node.js | Java |
|---|---|---|---|
| 拼接 | `Path("a") / "b"` | `path.join("a", "b")` | `Path.of("a", "b")` |
| 读文本 | `p.read_text(encoding="utf-8")` | `fs.readFileSync(p, "utf8")` | `Files.readString(p)` |
| 写文本 | `p.write_text(s, encoding="utf-8")` | `fs.writeFileSync(p, s)` | `Files.writeString(p, s)` |
| 递归查找 | `p.rglob("*.py")` | `fs.globSync`（Node 22+） | `Files.walk` |
| 脚本目录 | `Path(__file__).parent` | `import.meta.dirname` | — |

## 读代码

```python
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
for path in sorted(DATA_DIR.glob("*.json")):
    records = json.loads(path.read_text(encoding="utf-8"))
```

读到这类代码，先确定基准目录（`__file__` 还是 `cwd`），再看匹配模式（`glob` 还是 `rglob`）。

## 练习

### 练习 1：统计 Python 文件

实现 `count_py_lines(root)`：递归查找 `root` 下所有 `.py` 文件，返回 `{相对路径字符串: 行数}`。相对路径用 `path.relative_to(root).as_posix()`。

```python exercise id=s08-l01-count
# --- starter ---
from pathlib import Path

def count_py_lines(root):
    return {}
# --- solution ---
from pathlib import Path

def count_py_lines(root):
    root = Path(root)
    return {
        p.relative_to(root).as_posix(): len(p.read_text(encoding="utf-8").splitlines())
        for p in root.rglob("*.py")
    }
# --- check ---
from pathlib import Path
base = Path("demo_proj")
(base / "pkg").mkdir(parents=True, exist_ok=True)
(base / "main.py").write_text("import os\nprint(1)\n", encoding="utf-8")
(base / "pkg" / "tools.py").write_text("def f():\n    return 1\n\n", encoding="utf-8")
(base / "README.md").write_text("# x\n", encoding="utf-8")
got = count_py_lines(base)
assert got == {"main.py": 2, "pkg/tools.py": 3}, got
assert count_py_lines(str(base)) == got, "也应接受字符串路径"
```

### 练习 2：安全写入

实现 `save_note(directory, name, text)`：确保目录存在（可能是多级、尚不存在），把 `text` 以 UTF-8 写入 `directory/name`，返回该文件的 `Path`。

```python exercise id=s08-l01-save
# --- starter ---
from pathlib import Path

def save_note(directory, name, text):
    path = Path(directory) / name
    path.write_text(text, encoding="utf-8")
    return path
# --- solution ---
from pathlib import Path

def save_note(directory, name, text):
    path = Path(directory) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path
# --- check ---
p = save_note("notes/2026/10", "today.md", "# 今天\n学习 pathlib\n")
assert p.read_text(encoding="utf-8") == "# 今天\n学习 pathlib\n"
assert p.as_posix() == "notes/2026/10/today.md"
save_note("notes/2026/10", "today.md", "覆盖")
assert p.read_text(encoding="utf-8") == "覆盖"
```

## 小结

- `Path` 用 `/` 拼接，`.name/.stem/.suffix/.parent` 拆解。
- 读写文本始终 `encoding="utf-8"`；`mkdir(parents=True, exist_ok=True)` 创建目录。
- `glob` 当前层、`rglob` 递归；基准目录用 `Path(__file__).resolve().parent`。

## 延伸阅读

- [pathlib](https://docs.python.org/zh-cn/3/library/pathlib.html)
- [读写文件（教程）](https://docs.python.org/zh-cn/3/tutorial/inputoutput.html#reading-and-writing-files)
- [open() 内置函数](https://docs.python.org/zh-cn/3/library/functions.html#open)
