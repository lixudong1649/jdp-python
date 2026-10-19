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


## 易错点

- **`SettingWithCopy`**：`df[df.city == "上海"].temp = 0` 可能只改到临时副本；应使用 `df.loc[df.city == "上海", "temp"] = 0`。
- **读 CSV 全当字符串**：`read_csv` 可传 `dtype` 或 `converters`；否则聚合前要自己 `astype(float)`。
- **大表一次性读入**：`read_csv(chunksize=...)` 分块；笔记本里别对百万行反复 `apply` Python 函数。

```python run raises=KeyError
row = {"city": "上海", "humidity": "65%"}
expected_cols = ("city", "temp", "humidity")
print("当前行键", sorted(row.keys()))
print("期望列", expected_cols)
missing = [c for c in expected_cols if c not in row]
print("缺失列", missing)
if missing:
    print("访问缺失列 temp 前已发现缺口")
_ = row["temp"]
```

字典行缺 `temp` 却按完整 schema 去索引，会先打印现有键与缺失列名单，再触发 `KeyError`。这与 `DataFrame` 取不存在的列名失败类似，探索时应先 `columns`/`keys()` 再聚合。

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


## 小结

- DataFrame 是带标签的表；读代码先看 `columns`、`dtypes`、`shape`。
- `groupby` 是报告类任务的核心；课内用 dict 模拟，本地用 pandas 静态块对照。
- 赋值用 `loc` 避免 SettingWithCopy；读 CSV 注意类型。
- 阶段 21 项目测试命令：`uv run pytest examples/项目/21-CSV分析报告/test_analyze.py -q`。

## 延伸阅读

- [pandas IO：read_csv](https://pandas.pydata.org/docs/user_guide/io.html)
- [pandas groupby](https://pandas.pydata.org/docs/user_guide/groupby.html)
