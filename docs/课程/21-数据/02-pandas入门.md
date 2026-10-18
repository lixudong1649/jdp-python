---
title: 21.2 pandas 入门
---

# 21.2 pandas 入门

> 前置：21.1 NumPy · 约 25 分钟 · 官方对应：[pandas 入门](https://pandas.pydata.org/docs/getting_started/index.html)

## 目标

- 会用 DataFrame 读 CSV
- 会做 groupby 聚合

## 核心概念

```python run
import csv
from io import StringIO
from collections import defaultdict
text = "city,temp\n上海,22\n北京,18\n"
rows = list(csv.DictReader(StringIO(text)))
by = defaultdict(list)
for r in rows:
    by[r['city']].append(float(r['temp']))
print({k: sum(v)/len(v) for k,v in by.items()})
```

## 易错点

- SettingWithCopy 警告。
- 大表注意 dtype 与内存。

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 本节重点 | 见官方文档 | — | — |

## 读代码

报告型任务 pandas 一行 read_csv；读代码先看 columns 与 index。

## 练习

```python exercise id=s21-l02-pd
# --- starter ---
rows = [{'a': 1}]
val = rows[0].get('b')
# --- solution ---
rows = [{'a': 1}]
val = rows[0]['a']
# --- check ---
assert val == 1
```

## 小结

- DataFrame 像带标签表
- groupby 聚合

## 延伸阅读

- [pandas 文档](https://pandas.pydata.org/docs/)
