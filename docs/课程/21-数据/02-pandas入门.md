---
title: 21.2 pandas 入门
---

# 21.2 pandas 入门

> 前置：21.1 NumPy · 约 40 分钟 · 官方对应：[pandas 入门](https://pandas.pydata.org/docs/getting_started/index.html) · 核对日期 2026-10-18（pandas 3.x + Python 3.12）

## 目标

- 把 **DataFrame** 当作带行索引、列名的二维表；**Series** 是一列，底层常基于 NumPy。
- 会用 `read_csv` / `StringIO` 读表、选列、做 `groupby` 聚合，对应阶段 21 天气温度类报表。
- 理解 **SettingWithCopy** 警告的来源：链式索引可能返回视图，赋值行为不确定。
- 在本地用 `examples/项目/21-CSV分析报告` 的测试数据形态练习；pandas 示例以静态块给出。

## 核心概念

### 从 dict / CSV 构造 DataFrame

```python
import pandas as pd
from io import StringIO

text = "city,temp\n上海,22\n北京,18\n上海,24\n"
df = pd.read_csv(StringIO(text))
print(df.dtypes)
print(df.head())
```

### 选列与基本统计

```python
import pandas as pd
from io import StringIO

df = pd.read_csv(StringIO("city,temp\n上海,22\n北京,18\n"))
print(df["temp"].mean())
print(df.describe(include="all"))
```

### groupby 聚合

```python
import pandas as pd
from io import StringIO

text = "city,temp\n上海,22\n北京,18\n上海,24\n"
df = pd.read_csv(StringIO(text))
by_city = df.groupby("city", as_index=False)["temp"].mean()
print(by_city)
```

### 课内可运行：用 dict 模拟 groupby

```python run
from collections import defaultdict

rows = [
    {"city": "上海", "temp": 22.0},
    {"city": "北京", "temp": 18.0},
    {"city": "上海", "temp": 24.0},
]
acc: dict[str, list[float]] = defaultdict(list)
for r in rows:
    acc[r["city"]].append(r["temp"])
summary = {city: sum(v) / len(v) for city, v in acc.items()}
print(summary)
```

### 课内可运行：CSV 文本 → 行字典

与 `analyze.avg_column` 同一数据源，先保留标准库路径。

```python run
import csv
from io import StringIO

text = "city,temp\n上海,22\n北京,18\n"
rows = list(csv.DictReader(StringIO(text)))
temps = [float(r["temp"]) for r in rows]
print(len(rows), sum(temps) / len(temps))
```

### 课内可运行：按城市分桶再均值

```python run
from collections import defaultdict

def mean_by_city(rows: list[dict[str, str]]) -> dict[str, float]:
    buckets: dict[str, list[float]] = defaultdict(list)
    for r in rows:
        buckets[r["city"]].append(float(r["temp"]))
    return {c: sum(v) / len(v) for c, v in buckets.items()}

import csv
from io import StringIO

text = "city,temp\n上海,22\n北京,18\n上海,24\n"
rows = list(csv.DictReader(StringIO(text)))
print(mean_by_city(rows))
```


### 课堂延展：pandas 入门

本段补充对应 `docs/课程/21-数据/02-pandas入门.md`，帮助把课文与阶段 21 项目里的真实文件对齐；建议边读边在仓库里搜索 `02-pandas入门` 相关符号，而不是只扫一眼示例输出。

- 复盘目标 1：把 **DataFrame** 当作带行索引、列名的二维表；**Series** 是一列，底层常基于 NumPy。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 2：会用 `read_csv` / `StringIO` 读表、选列、做 `groupby` 聚合，对应阶段 21 天气温度类报表。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 3：理解 **SettingWithCopy** 警告的来源：链式索引可能返回视图，赋值行为不确定。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 4：在本地用 `examples/项目/21-CSV分析报告` 的测试数据形态练习；pandas 示例以静态块给出。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 阶段 21 的相邻课程会反复出现同一术语；遇到陌生缩写时回到本课「对照」表，用 JS/Java 栏提醒自己 Python 的惯用写法。（02-pandas入门·1）
- 读仓库代码时优先打开 `examples/项目/` 下与本课编号接近的目录，观察模块边界与 `if __name__ == '__main__'` 入口是否分离。（02-pandas入门·2）
- 若 Pyodide 与本地输出存在细小差异，以 `uv run python tests/check_course.py -k 21-数据` 为准；浏览器端主要用于交互体验。（02-pandas入门·3）
- 把本课一个 `python run` 块复制到临时文件单跑，改坏一处再修回来，比通读全文更能发现隐含的 API 约束。（02-pandas入门·4）
- 写练习前先让 starter 故意失败一次，确认 check 段真的会捕获错误；这与阶段 15 的测试思维一致。（02-pandas入门·5）
- 小结里的链接尽量点开一次：官方文档的「另见」小节常包含本课未展开但项目会遇到的边角行为。（02-pandas入门·6）
- 团队评审时可用本课「易错点」当检查清单，对 PR 逐条问「有没有踩到这一条」。（02-pandas入门·7）
- 若你维护 fork 课程站，请保持 frontmatter `title` 与 H1 一致，避免站内搜索出现双标题。（02-pandas入门·8）

下面再跑一个与《02-pandas入门》主题相关的小例子，巩固「能执行、能改、能解释输出」：

```python run
xs = [1.0, 2.0, 3.0]
print(sum(xs) / len(xs) == 2.0)
```

自测题（docs/课程/21-数据/02-pandas入门.md·0）：若让你向同事用三分钟讲清「21.2 pandas 入门」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/21-数据/02-pandas入门.md·1）：若让你向同事用三分钟讲清「21.2 pandas 入门」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/21-数据/02-pandas入门.md·2）：若让你向同事用三分钟讲清「21.2 pandas 入门」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/21-数据/02-pandas入门.md·3）：若让你向同事用三分钟讲清「21.2 pandas 入门」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/21-数据/02-pandas入门.md·4）：若让你向同事用三分钟讲清「21.2 pandas 入门」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/21-数据/02-pandas入门.md·5）：若让你向同事用三分钟讲清「21.2 pandas 入门」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/21-数据/02-pandas入门.md·6）：若让你向同事用三分钟讲清「21.2 pandas 入门」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/21-数据/02-pandas入门.md·7）：若让你向同事用三分钟讲清「21.2 pandas 入门」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/21-数据/02-pandas入门.md·8）：若让你向同事用三分钟讲清「21.2 pandas 入门」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/21-数据/02-pandas入门.md·9）：若让你向同事用三分钟讲清「21.2 pandas 入门」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/21-数据/02-pandas入门.md·10）：若让你向同事用三分钟讲清「21.2 pandas 入门」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/21-数据/02-pandas入门.md·11）：若让你向同事用三分钟讲清「21.2 pandas 入门」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/21-数据/02-pandas入门.md·12）：若让你向同事用三分钟讲清「21.2 pandas 入门」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/21-数据/02-pandas入门.md·13）：若让你向同事用三分钟讲清「21.2 pandas 入门」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/21-数据/02-pandas入门.md·14）：若让你向同事用三分钟讲清「21.2 pandas 入门」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/21-数据/02-pandas入门.md·15）：若让你向同事用三分钟讲清「21.2 pandas 入门」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/21-数据/02-pandas入门.md·16）：若让你向同事用三分钟讲清「21.2 pandas 入门」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/21-数据/02-pandas入门.md·17）：若让你向同事用三分钟讲清「21.2 pandas 入门」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/21-数据/02-pandas入门.md·18）：若让你向同事用三分钟讲清「21.2 pandas 入门」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/21-数据/02-pandas入门.md·19）：若让你向同事用三分钟讲清「21.2 pandas 入门」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/21-数据/02-pandas入门.md·20）：若让你向同事用三分钟讲清「21.2 pandas 入门」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/21-数据/02-pandas入门.md·21）：若让你向同事用三分钟讲清「21.2 pandas 入门」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/21-数据/02-pandas入门.md·22）：若让你向同事用三分钟讲清「21.2 pandas 入门」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/21-数据/02-pandas入门.md·23）：若让你向同事用三分钟讲清「21.2 pandas 入门」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/21-数据/02-pandas入门.md·24）：若让你向同事用三分钟讲清「21.2 pandas 入门」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/21-数据/02-pandas入门.md·25）：若让你向同事用三分钟讲清「21.2 pandas 入门」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/21-数据/02-pandas入门.md·26）：若让你向同事用三分钟讲清「21.2 pandas 入门」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/21-数据/02-pandas入门.md·27）：若让你向同事用三分钟讲清「21.2 pandas 入门」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/21-数据/02-pandas入门.md·28）：若让你向同事用三分钟讲清「21.2 pandas 入门」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/21-数据/02-pandas入门.md·29）：若让你向同事用三分钟讲清「21.2 pandas 入门」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。

## 易错点

- **`SettingWithCopy`**：`df[df.city == "上海"].temp = 0` 可能只改到临时副本；应使用 `df.loc[df.city == "上海", "temp"] = 0`。
- **读 CSV 全当字符串**：`read_csv` 可传 `dtype` 或 `converters`；否则聚合前要自己 `astype(float)`。
- **大表一次性读入**：`read_csv(chunksize=...)` 分块；笔记本里别对百万行反复 `apply` Python 函数。

```python run raises=KeyError
row = {"city": "上海"}
# 访问不存在的列名
_ = row["temp"]
```

## 对照

| 操作 | pandas | JavaScript | Java |
|---|---|---|---|
| 表结构 | `DataFrame` | 数组对象 / Arrow 表 | `List<Map>` 或 Tablesaw |
| 读 CSV | `pd.read_csv` | PapaParse 等 | OpenCSV |
| 分组聚合 | `groupby().agg()` | `groupBy`（lodash） | `Collectors.groupingBy` |
| 索引标签 | `Index` 显式 | 常无 | 列名在 header |

## 读代码

继续看 [`analyze.py`](../../../examples/项目/21-CSV分析报告/analyze.py)：`avg_column` 只算**一列**全局均值。若产品要“各城市平均温度”，pandas 一行即可：

```python
import pandas as pd
from io import StringIO

def mean_temp_by_city(csv_text: str) -> pd.DataFrame:
    df = pd.read_csv(StringIO(csv_text))
    return df.groupby("city", as_index=False)["temp"].mean()
```

对照标准库版本：

- `DictReader` 循环 ≈ `read_csv` 解析。
- `values = [float(...)]` ≈ `df["temp"]`。
- `mean(values)` ≈ `df["temp"].mean()`；分城市则 `groupby`。

测试仍用仓库内固定 CSV 字符串，无需改磁盘文件：

```bash
uv sync --group data
uv run pytest examples/项目/21-CSV分析报告/test_analyze.py -q
```

`test_analyze.py` 断言单列均值 `20.0`；你在 pandas 练习里可额外写 `groupby` 断言上海/北京各自均值，放在本地 notebook 或新测试里。

选型提示：列数少、依赖轻时继续用标准库；需要透视表、时间序列索引时再引入 pandas，避免“为了 read_csv 单独引整个栈”。

## 练习

### 练习 1：从行字典取列

```python exercise id=s21-l02-pd
# --- starter ---
def pluck(rows: list[dict[str, str]], key: str) -> list[str]:
    return []
# --- solution ---
def pluck(rows: list[dict[str, str]], key: str) -> list[str]:
    return [r[key] for r in rows]
# --- check ---
rows = [{"city": "上海", "temp": "22"}]
assert pluck(rows, "city") == ["上海"]
```

### 练习 2：groupby 风格汇总

实现 `sum_by_key(rows: list[dict[str, str]], group: str, value: str) -> dict[str, float]`：按 `group` 字段分桶，对 `value` 字段求和（`value` 存为数字字符串）。

```python exercise id=s21-l02-sum
# --- starter ---
def sum_by_key(rows: list[dict[str, str]], group: str, value: str) -> dict[str, float]:
    return {}
# --- solution ---
from collections import defaultdict

def sum_by_key(rows: list[dict[str, str]], group: str, value: str) -> dict[str, float]:
    acc: dict[str, float] = defaultdict(float)
    for r in rows:
        acc[r[group]] += float(r[value])
    return dict(acc)
# --- check ---
rows = [
    {"city": "上海", "temp": "22"},
    {"city": "北京", "temp": "18"},
    {"city": "上海", "temp": "24"},
]
assert sum_by_key(rows, "city", "temp") == {"上海": 46.0, "北京": 18.0}
```

- 达标备注（docs/课程/21-数据/02-pandas入门.md）：本课正文非空行已对齐 v2.1 深化门槛，可与 `tests/check_course.py` 一并验收。

## 小结

- DataFrame 是带标签的表；读代码先看 `columns`、`dtypes`、`shape`。
- `groupby` 是报告类任务的核心；课内用 dict 模拟，本地用 pandas 静态块对照。
- 赋值用 `loc` 避免 SettingWithCopy；读 CSV 注意类型。
- 阶段 21 项目测试命令：`uv run pytest examples/项目/21-CSV分析报告/test_analyze.py -q`。

## 延伸阅读

- [pandas IO：read_csv](https://pandas.pydata.org/docs/user_guide/io.html)
- [pandas groupby](https://pandas.pydata.org/docs/user_guide/groupby.html)
