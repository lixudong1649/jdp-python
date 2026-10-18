---
title: 14.1 编码与 bytes
---

# 14.1 编码与 bytes

> 前置：2.3 字符串 · 约 35 分钟 · 官方对应：[文本与二进制序列类型](https://docs.python.org/zh-cn/3/library/stdtypes.html#text-sequence-type-str)、[二进制序列类型](https://docs.python.org/zh-cn/3/library/stdtypes.html#binary-sequence-types-bytes-bytearray-memoryview)

## 目标

- 分清 **str**（Unicode 文本）与 **bytes**（原始字节序列），知道在磁盘与网络边界上必须编码/解码。
- 用 `encode` / `decode` 显式指定 **UTF-8**，并理解 `errors=` 在脏数据时的行为。
- 读写文本文件时始终写 `encoding="utf-8"`，与阶段项目 `logstats` 的读文件方式一致。
- 知道 `bytes` 字面量、`bytearray` 可变性，以及何时用二进制模式 `rb`/`wb`。

## 核心概念

### str 与 bytes 各管什么

Python 3 里字符串在内存中是 Unicode 码点序列；**bytes** 是 0–255 的不可变字节序列。二者不能混用：不能把 `str` 直接写入只接受 `bytes` 的 API，也不能把 `bytes` 当作文本拼接。

```python run
text = "上海"
raw = text.encode("utf-8")          # str → bytes，按 UTF-8 规则变成字节
back = raw.decode("utf-8")          # bytes → str
print(type(text), type(raw))
print(raw)                            # b'\xe4\xb8\x8a\xe6\xb5\xb7'
print(len(text), len(raw))            # 2 个字符 vs 6 个字节
print(back == text)
```

`b'...'` 是 **bytes 字面量**，里面只能是 ASCII 范围内的字符；非 ASCII 文本要先写 `str` 再 `.encode()`。

### bytearray 与不可变 bytes

需要原地改几个字节时用 `bytearray`；算哈希、作为 dict 键时仍要 `bytes`。

```python run
buf = bytearray(b"abc")
buf[0] = ord("A")
print(bytes(buf))
print(hash(b"abc"))
```

网络协议里常见“长度前缀 + 载荷”：载荷部分是 bytes，头部字段解析完再 `.decode("ascii")` 成 str。

### 编码名称与 BOM

常见编码名：`utf-8`（推荐）、`utf-8-sig`（读带 BOM 的 UTF-8 时会去掉 BOM）、`latin-1`（一字节一码点，适合“当作原始字节”的兜底解码）。

```python run
bom = "\ufeff标题".encode("utf-8-sig")
plain = bom.decode("utf-8-sig")
print(repr(plain), plain[0])
```

### 解码失败与 errors=

默认 `decode` 遇到非法字节会抛 `UnicodeDecodeError`。日志、爬虫、旧系统文件里常有脏字节，可按场景选择策略（生产环境慎用盲目 `ignore`）。

```python run raises=UnicodeDecodeError
bad = b"\xff\xfe"
bad.decode("utf-8")
```

```python run
bad = b"ok\xfftail"
print(bad.decode("utf-8", errors="replace"))   # 非法字节变成 U+FFFD
print(bad.decode("latin-1"))                   # 每字节对应一个 Unicode 码点
```

### 与文件 I/O 的关系

- **文本模式**：`open(..., encoding="utf-8")` 或 `Path.read_text(encoding="utf-8")` 读入 **str**，写出时同样编码。
- **二进制模式**：`read_bytes()` / `"rb"` 得到 **bytes**，适合图片、压缩包、或你自己处理编码的场景。

```python run
from pathlib import Path

p = Path("sample_utf8.txt")
p.write_text("第一行\n第二行\n", encoding="utf-8")
print(p.read_text(encoding="utf-8").splitlines())
print(p.read_bytes()[:10])
```

阶段 14 项目 `logstats` 用一行读完整份日志为 str，后面正则就在 str 上工作——前提是文件确实是 UTF-8 文本。

### 核对环境（核对日期 2026-10-18）

课程仓库 `.python-version` 固定 **3.12**；`str` / `bytes` 语义在 3.12–3.15 一致。Windows 记事本“UTF-8”与 Python `utf-8` 通常兼容；若文件来自旧系统，先用十六进制查看器确认是否有 BOM 或混合编码，再决定 `encoding` 或 `errors=`。

```python run
import sys

print(sys.version_info[:2])
print("defaultfilesystemencoding", sys.getdefaultencoding())
```


## 易错点

- **不指定 encoding**：`open(path)` 的默认编码依赖系统区域设置，在 Windows 上常不是 UTF-8，中文容易乱码或 silently 用错误编码读入。
- **把 `str` 和 `bytes` 比较或拼接**：`"a" + b"b"` 会 `TypeError`；先统一一侧。
- **误以为 `len(str)` 等于 UTF-8 字节数**：一个 emoji 或汉字可能占多个字节。
- **用 `str(bytes_obj)` 当解码**：会得到 `"b'...'"` 这种调试表示，不是文本内容；要用 `.decode()`。
- **JSON 与文本**：`json.dumps` 产出 str；`httpx` 的 `response.content` 是 bytes，需要 `.text` 或 `.json()`（内部会解码）。
- **子进程输出**：`subprocess.run(..., text=True, encoding="utf-8")` 直接得到 str；`text=False` 时自己 `.decode()`。

```python run
payload = "ok".encode("utf-8")
assert payload.decode("utf-8") == "ok"
```

```python run raises=TypeError
"a" + b"b"
```

## 对照

| 场景 | Python | Node.js | Java |
|---|---|---|---|
| 文本类型 | `str` | `string` | `String` |
| 字节类型 | `bytes` | `Buffer` / `Uint8Array` | `byte[]` |
| 编码 | `s.encode("utf-8")` | `Buffer.from(s, "utf8")` | `s.getBytes(StandardCharsets.UTF_8)` |
| 读文本文件 | `Path.read_text(encoding="utf-8")` | `fs.readFileSync(p, "utf8")` | `Files.readString(p, UTF_8)` |
| 读二进制 | `Path.read_bytes()` | `fs.readFileSync(p)` | `Files.readAllBytes(p)` |

## 读代码

阶段项目 [`examples/项目/14-日志统计CLI/logstats.py`](../../../examples/项目/14-日志统计CLI/logstats.py) 在 `main` 里把日志文件读成 **str**，再交给 `parse_lines`：

```python
text = args.file.read_text(encoding="utf-8")
counts = parse_lines(text)
```

读这段时要抓住三点：

1. **`args.file` 是 `pathlib.Path`**（由 `argparse` 的 `type=Path` 转换），所以能用 `read_text`，而不是手动 `open`。
2. **`encoding="utf-8"` 是显式约定**：与课程 8.1 一致，避免依赖系统默认编码；若日志是 GBK，这里应改成对应编码或先 `read_bytes()` 再尝试检测（本项目假设 UTF-8）。
3. **整文件读入内存**：适合教学用的小日志；超大文件应改为按行迭代 `for line in path.open(encoding="utf-8")`，正则仍可对每行 `search`。

`parse_lines` 的参数类型注解是 `text: str`，说明解析层不关心字节——编码边界在 **读文件** 这一步已经处理完。

本地试跑（项目根目录）：

```bash
uv run python examples/项目/14-日志统计CLI/logstats.py path/to.log
```

若 `read_text` 抛出 `UnicodeDecodeError`，说明文件字节不是合法 UTF-8：要么换 `encoding`，要么用 `errors="replace"` 并记录数据质量，而不是在 `parse_lines` 里硬修。

### 与正则、CLI 的衔接

同一条日志流水线是：**Path → str（本课）→ 行与正则（14.2）→ Counter 与打印（14.4）**。编码选错时，正则仍可能“跑通”，但中文路径或消息会变成乱码，统计结果不可信。养成习惯：打开文件的第一行代码就写 `encoding="utf-8"`。

## 练习

### 练习 1：encode 成 UTF-8

```python exercise id=s14-l01-bytes
# --- starter ---
s = "a"
# --- solution ---
s = "a"
b = s.encode("utf-8")
# --- check ---
assert b == b"a"
```

### 练习 2：往返解码

实现 `utf8_roundtrip(text: str) -> bool`：判断 `text.encode("utf-8").decode("utf-8") == text` 是否成立。

```python exercise id=s14-l01-roundtrip
# --- starter ---
def utf8_roundtrip(text: str) -> bool:
    return False
# --- solution ---
def utf8_roundtrip(text: str) -> bool:
    return text.encode("utf-8").decode("utf-8") == text
# --- check ---
assert utf8_roundtrip("上海") is True
assert utf8_roundtrip("") is True
```

### 练习 3：bytes 字面量长度

```python exercise id=s14-l01-len
# --- starter ---
b = b"ab"
# --- solution ---
b = b"ab"
n = len(b)
# --- check ---
assert n == 2
```


## 小结

- 文本在 Python 里是 **str**；落盘、套接字、多数 crypto API 要 **bytes**。
- 阶段 14 起所有示例项目默认 **UTF-8 文本日志**；换编码是破坏性变更，要同时改文档与测试数据。
- 读代码时先找 `read_text` / `read_bytes` / `.encode` 三处之一，再往下看业务逻辑。
- **UTF-8** 是跨平台默认首选；读写文件写全 `encoding="utf-8"`。
- `encode` / `decode` 成对出现；脏数据用 `errors=` 要有意为之，而不是默默吞掉。
- `logstats` 在 `read_text` 处完成编码决策，后面正则只处理 str。
- 下一课在 str 上用 `re` 提取日志级别，不再碰 bytes。

## 延伸阅读

- [Unicode HOWTO](https://docs.python.org/zh-cn/3/howto/unicode.html)
- [标准类型：str 与 bytes](https://docs.python.org/zh-cn/3/library/stdtypes.html#text-sequence-type-str)
