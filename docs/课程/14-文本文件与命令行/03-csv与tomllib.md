---
title: 14.3 csv 与 tomllib
---

# 14.3 csv 与 tomllib

> 前置：4.2 字典 · 约 35 分钟 · 官方对应：[csv](https://docs.python.org/zh-cn/3/library/csv.html)、[tomllib](https://docs.python.org/zh-cn/3/library/tomllib.html)

## 目标

- 用 `csv` 模块读写表格数据：行列表、`DictReader` / `DictWriter`，以及 **`newline=""`** 打开文件的原因。
- 用 **`tomllib`**（标准库，Python 3.11 起）只读解析 TOML，对照本仓库 `pyproject.toml` 的结构。
- 区分 CSV（行/列、分隔符）与 TOML（层级表、类型），避免把二者当成 JSON 用。
- 能把 `Counter` 统计结果导出为 CSV，作为 `logstats` 的自然扩展。

## 核心概念

### csv.reader：按行解析

`csv.reader` 接受可迭代对象（文件对象或 `StringIO`），每次迭代得到 **字符串列表**（一行一列）。

```python run
import csv
from io import StringIO

buf = StringIO("name,score\nAda,98\nBob,87\n")
rows = list(csv.reader(buf))
print(rows)
print(rows[1][0], rows[1][1])
```

### csv.writer 与 quoting

写出时同样用 `writerow` / `writerows`；字段里若含逗号、引号，模块会按 RFC 规则加引号。

```python run
import csv
from io import StringIO

out = StringIO()
w = csv.writer(out)
w.writerow(["city", "temp"])
w.writerow(["上海", 22])
print(out.getvalue())
```

### DictReader：首行当表头

日志统计导出时常用“级别,次数”两列；读入带表头的 CSV 时，`DictReader` 把每行变成 `dict`。

```python run
import csv
from io import StringIO

buf = StringIO("level,count\nINFO,3\nERROR,1\n")
for row in csv.DictReader(buf):
    print(row["level"], row["count"])
```

### 写文件时必须 newline=""

文档要求：在 **文本模式** 下 `open(path, newline="")` 再交给 `csv.reader`/`writer`，否则 `\r\n` 平台上可能出现多余空行。核对日期 2026-10-18：课程项目固定 **Python 3.12**，`tomllib` 已内置。

```python run
import csv
from pathlib import Path

p = Path("counts.csv")
with p.open("w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["level", "count"])
    w.writerow(["INFO", 3])
print(p.read_text(encoding="utf-8"))
p.unlink(missing_ok=True)
```

### tomllib：只读 TOML

`tomllib.load(二进制文件对象)` 解析 TOML 为嵌套 `dict`。`pyproject.toml` 是工具链入口，读版本、依赖时常用。

```python run
import tomllib
from io import BytesIO

data = b"""
[project]
name = "demo"
version = "0.1.0"
requires-python = ">=3.12"
"""
info = tomllib.load(BytesIO(data))
print(info["project"]["name"], info["project"]["requires-python"])
```

TOML 不是 JSON：键名可带点号表、有日期/内联表等语法；**没有** 标准库 `tomli_w` 写回，修改配置一般用编辑器或专门工具。

### 与 logstats 输出衔接

`parse_lines` 返回 `Counter`；若要交给 Excel 或 BI 工具，可写：

```python run
import csv
from collections import Counter
from io import StringIO

counts = Counter({"INFO": 2, "ERROR": 1})
buf = StringIO()
w = csv.writer(buf)
w.writerow(["level", "count"])
for level in ("DEBUG", "INFO", "WARNING", "ERROR"):
    if counts[level]:
        w.writerow([level, counts[level]])
print(buf.getvalue())
```


## 易错点

- **忘记 `newline=""`**：在 Windows 上写 CSV 容易出现奇怪换行；读一般也建议加上。
- **把 CSV 当强类型**：读出来全是 `str`；数字要自己 `int(row["count"])`。
- **用 `json.loads` 读 TOML**：会失败；TOML 允许无引号键、禁止尾随逗号等规则与 JSON 不同。
- **`tomllib` 需要二进制文件**：`open(path, "rb")`；文本模式 `read_text` 要先 `encode` 或改用 `bytes` 路径 API。
- **超大 CSV**：不要 `list(reader)` 一次载入；逐行处理或考虑 `pandas`（阶段 21）。

## 对照

| 格式 | 典型用途 | Python 读 | Python 写 |
|---|---|---|---|
| CSV | 表格、导出 | `csv.reader` / `DictReader` | `csv.writer` + `newline=""` |
| TOML | `pyproject.toml` | `tomllib.load`（3.11+） | 无标准库写（用工具或手工） |
| JSON | API、消息 | `json.loads` | `json.dumps` |

| 操作 | Python | Node.js | Java |
|---|---|---|---|
| CSV 解析 | `csv` 模块 | `csv-parse` 等 | OpenCSV / Commons CSV |
| 配置 TOML | `tomllib` | `@iarna/toml` | `toml4j` 等 |

## 读代码

`logstats.py` 本身不读 CSV/TOML，但和本课有两条实线：

1. **项目元数据**：仓库根 `pyproject.toml` 声明 `requires-python`、依赖；用 `tomllib` 可在小脚本里读版本约束，而不用引第三方解析器（Python 3.12 下核对日期 2026-10-18 已满足）。

```python
import tomllib
from pathlib import Path

root = Path(__file__).resolve().parents[3]  # 示例：从 examples/... 回到仓库根
data = tomllib.loads(root.joinpath("pyproject.toml").read_bytes())
print(data.get("project", {}).get("name"))
```

2. **统计结果形态**：`main` 打印 `level: count` 文本；若产品要“可导入表格”，在 `counts = parse_lines(text)` 之后用上一节的 `csv.writer` 写 `level,count` 即可，列顺序可与 `main` 里 `("DEBUG", "INFO", "WARNING", "ERROR")` 保持一致。

读 `test_logstats.py` 时只有内存字符串，没有文件格式问题；集成测试阶段才会碰到 `read_text` + CSV 导出组合。

### 选型备忘

- 需要 Excel 双击打开、列稳定：CSV + UTF-8，必要时带 BOM 的 `utf-8-sig` 写首行（仅当目标工具要求）。
- 需要嵌套配置、人类可编辑：TOML（`pyproject.toml`）优于 CSV。
- 需要 API 互通：JSON（见 8.2），不要强行用 CSV 表达树形结构。

## 练习

### 练习 1：reader 读首列

```python exercise id=s14-l03-csv
# --- starter ---
row = ["y"]
# --- solution ---
import csv
from io import StringIO

buf = StringIO("x\n1\n")
row = next(csv.reader(buf))
# --- check ---
assert row == ["x"]
```

### 练习 2：DictReader 取 count

实现 `sum_counts(csv_text: str) -> int`：解析带表头 `level,count` 的 CSV，把所有 `count` 列求和（当作整数）。

```python exercise id=s14-l03-sum
# --- starter ---
def sum_counts(csv_text: str) -> int:
    return 0
# --- solution ---
import csv
from io import StringIO

def sum_counts(csv_text: str) -> int:
    total = 0
    for row in csv.DictReader(StringIO(csv_text)):
        total += int(row["count"])
    return total
# --- check ---
text = "level,count\nINFO,2\nERROR,1\n"
assert sum_counts(text) == 3
```


## 小结

- CSV 处理记住 **`encoding="utf-8"`** 与 **`newline=""`** 这一对组合。
- `DictReader` 适合有表头的导出/导入；纯一列可用 `reader`。
- `tomllib` 只读，适合读 `pyproject.toml`；写配置仍靠编辑或构建工具。
- `logstats` 的 `Counter` 很容易延伸为 CSV 报表，而不改解析逻辑。

## 延伸阅读

- [csv 模块](https://docs.python.org/zh-cn/3/library/csv.html)
- [tomllib 模块](https://docs.python.org/zh-cn/3/library/tomllib.html)
- [TOML v1.0 规范（PEP 680 引入 tomllib）](https://peps.python.org/pep-0680/)
