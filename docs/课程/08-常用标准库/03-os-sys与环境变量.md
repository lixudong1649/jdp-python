---
title: 8.3 os、sys 与环境变量
---

# 8.3 os、sys 与环境变量

> 前置：8.1 · 约 25 分钟 · 官方对应：[os.environ](https://docs.python.org/zh-cn/3/library/os.html#os.environ)、[sys](https://docs.python.org/zh-cn/3/library/sys.html)

## 目标

- 用 `os.environ` / `os.getenv` 读取环境变量，理解两者在缺失时的区别。
- 理解 `.env` 文件 + `load_dotenv()` 的机制，以及为什么密钥不写进代码。
- 读懂 `sys.argv`、`sys.exit`、`sys.stderr` 的用法。

## 核心概念

### 环境变量

环境变量是进程从父进程（如终端）继承的一组“名字=字符串值”。`os.environ` 是一个类似 dict 的映射：

```python run
import os

os.environ["LLM_PROVIDER"] = "anthropic"          # 设置（只影响当前进程及其子进程）
print(os.environ["LLM_PROVIDER"])                 # 缺失时抛 KeyError
print(os.getenv("LLM_PROVIDER"))                  # 缺失时返回 None
print(os.getenv("NOT_SET"), os.getenv("NOT_SET", "默认值"))
print(os.environ.get("NOT_SET", "也可以用 get"))
print("LLM_PROVIDER" in os.environ)
del os.environ["LLM_PROVIDER"]
print(os.getenv("LLM_PROVIDER"))
```

| 写法 | 缺失时 | 适用 |
|---|---|---|
| `os.environ["K"]` | 抛 `KeyError` | 必需配置：缺了立即失败 |
| `os.getenv("K")` | `None` | 可选配置 |
| `os.getenv("K", "默认")` | 返回默认值 | 有合理默认值的配置 |

注意：环境变量的值**永远是字符串**。`MAX_TURNS=5` 读到的是 `"5"`，需要 `int(...)`；布尔值要自己解析。

```python run
import os

os.environ["MAX_TURNS"] = "5"
os.environ["DEBUG"] = "false"
max_turns = int(os.getenv("MAX_TURNS", "3"))
debug = os.getenv("DEBUG", "").lower() in ("1", "true", "yes")
print(max_turns + 1, debug, bool("false"))        # bool("false") 是 True！
```

### .env 与 load_dotenv

`.env` 文件是一个约定：每行 `KEY=VALUE`。第三方包 `python-dotenv` 的 `load_dotenv()` 读取它，把其中的键值放入 `os.environ`（**默认不覆盖已存在的环境变量**），之后代码统一用 `os.getenv` 读取。

```text
# .env（不提交到版本库）
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-...
```

为什么这样做：

- 密钥不出现在代码中，代码可以公开、分享。
- `.env` 被 `.gitignore` 忽略；仓库中只提交不含真实值的模板 `.env.example`。
- 同一份代码在不同环境（本机、服务器、CI）读取不同配置。

下面用标准库模拟 `load_dotenv` 的核心行为：

```python run
import os

def load_env_text(text, override=False):
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = (part.strip() for part in line.split("=", 1))
        if override or key not in os.environ:
            os.environ[key] = value

os.environ["LLM_PROVIDER"] = "anthropic"            # 终端里已设置
load_env_text("LLM_PROVIDER=deepseek\nLLM_MODEL=deepseek-flash")
print(os.getenv("LLM_PROVIDER"), os.getenv("LLM_MODEL"))   # 已存在的不被覆盖
```

### sys：解释器与命令行

```python run
import sys

print(sys.argv)                       # 命令行参数列表；sys.argv[0] 是脚本名
print(sys.platform)                   # 'darwin'、'linux'、'win32'、浏览器中为 'emscripten'
print("错误信息写到 stderr", file=sys.stderr)
```

`sys.exit(code)` / `raise SystemExit(code)` 结束程序：`0` 表示成功，非零表示失败；传入字符串时打印到 stderr 并以 1 退出。命令行工具常这样写：

```python
import os
import sys

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    sys.exit("缺少 DEEPSEEK_API_KEY：请复制 .env.example 为 .env 并填写")
```

## 易错点

- **把环境变量当成数字或布尔值**：它们都是字符串，`bool("false")` 为 `True`。
- **以为 `os.environ[...] = ...` 会改变终端的环境**：只影响当前进程和它启动的子进程。
- **打印或记录密钥**：调试时只打印是否存在或前几位，如 `bool(api_key)`。
- **`load_dotenv()` 没生效**：`.env` 不在查找路径上（它从调用文件所在目录逐级向上查找），或变量已在终端中设置（默认不覆盖）。

```python run raises=KeyError
import os

api_key = os.environ["SOME_UNSET_API_KEY"]
```

## 对照

| 操作 | Python | Node.js | Java |
|---|---|---|---|
| 读取 | `os.getenv("K")` | `process.env.K` | `System.getenv("K")` |
| 缺失时 | `None` | `undefined` | `null` |
| .env | `python-dotenv` | `dotenv` / Node 20+ `--env-file` | 框架配置（如 Spring） |
| 命令行参数 | `sys.argv` | `process.argv` | `main(String[] args)` |
| 退出 | `sys.exit(1)` | `process.exit(1)` | `System.exit(1)` |

## 读代码

```python
from dotenv import load_dotenv

load_dotenv()                                            # ① 读取 .env → os.environ

provider = os.getenv("LLM_PROVIDER") or "deepseek"       # ② 可选配置，带默认值
config = PROVIDERS[provider]
model = os.getenv("LLM_MODEL") or config["model"]
client = anthropic.Anthropic(
    api_key=os.getenv(config["key_env"]),                # ③ 间接读取：变量名本身来自配置
    base_url=config["base_url"],
)
```

第 ③ 步很巧妙：`config["key_env"]` 是字符串 `"DEEPSEEK_API_KEY"`，再用它作为名字去读环境变量。

若该变量缺失，传给 SDK 的是 `api_key=None`。本项目锁定的 `anthropic` 1.11.0 中（`anthropic/_client.py`，核对日期 2026-10-06），没有显式凭据时客户端会**退回读取 `ANTHROPIC_API_KEY` / `ANTHROPIC_AUTH_TOKEN` 环境变量**；都没有时，直到发送请求才报 “Could not resolve authentication method”。换言之：使用 DeepSeek 却漏配 `DEEPSEEK_API_KEY`、而终端里恰好有 `ANTHROPIC_API_KEY` 时，会把 Anthropic 的密钥发给 DeepSeek 端点。这类行为只能靠读源码发现，10.4 会演示如何定位。

## 练习

### 练习 1：读取类型化配置

实现 `read_settings(env)`（`env` 是模拟 `os.environ` 的 dict）：返回 `(max_turns, debug)`。`MAX_TURNS` 缺失或为空时为 `5`，否则转为 `int`；`DEBUG` 取值（忽略大小写）为 `"1"`、`"true"`、`"yes"` 之一时为 `True`，其余为 `False`。

```python exercise id=s08-l03-settings
# --- starter ---
def read_settings(env):
    return env.get("MAX_TURNS", 5), bool(env.get("DEBUG"))
# --- solution ---
def read_settings(env):
    max_turns = int(env.get("MAX_TURNS") or 5)
    debug = env.get("DEBUG", "").lower() in ("1", "true", "yes")
    return max_turns, debug
# --- check ---
assert read_settings({}) == (5, False)
assert read_settings({"MAX_TURNS": "8", "DEBUG": "TRUE"}) == (8, True)
assert read_settings({"MAX_TURNS": "", "DEBUG": "false"}) == (5, False), "DEBUG=false 应为 False"
assert read_settings({"DEBUG": "0"}) == (5, False)
```

### 练习 2：不泄露密钥

实现 `mask(secret)`：`None` 或空串返回 `"<未设置>"`；长度不超过 8 返回 `"****"`；否则返回前 4 位 + `"…"` + 后 2 位。

```python exercise id=s08-l03-mask
# --- starter ---
def mask(secret):
    return secret
# --- solution ---
def mask(secret):
    if not secret:
        return "<未设置>"
    if len(secret) <= 8:
        return "****"
    return f"{secret[:4]}…{secret[-2:]}"
# --- check ---
assert mask(None) == "<未设置>" and mask("") == "<未设置>"
assert mask("short") == "****"
assert mask("sk-1234567890ab") == "sk-1…ab", mask("sk-1234567890ab")
```

## 小结

- `os.environ["K"]` 缺失抛错，`os.getenv("K")` 返回 `None`；值都是字符串。
- `.env` + `load_dotenv()`：配置与代码分离，密钥不进代码库；默认不覆盖已有变量。
- `sys.argv` 取命令行参数，`sys.exit` 设置退出码。

## 延伸阅读

- [os.environ 与 os.getenv](https://docs.python.org/zh-cn/3/library/os.html#os.environ)
- [sys 模块](https://docs.python.org/zh-cn/3/library/sys.html)
- [命令行与环境（PYTHON* 环境变量）](https://docs.python.org/zh-cn/3/using/cmdline.html#environment-variables)
- [argparse 教程](https://docs.python.org/zh-cn/3/howto/argparse.html)
