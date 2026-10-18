---
title: 14.3 csv 与 tomllib
---

# 14.3 csv 与 tomllib

> 前置：4.2 字典 · 约 25 分钟 · 官方对应：[csv](https://docs.python.org/zh-cn/3/library/csv.html)

## 目标

- 用 csv 模块读写表格
- 知道 tomllib 读 pyproject（3.11 起标准库）

## 核心概念

```python run
import csv
from io import StringIO
buf = StringIO("a,b\n1,2\n")
rows = list(csv.reader(buf))
print(rows)
```

## 易错点

- 未指定 newline='' 时 csv 可能行为异常。
- TOML 不是 JSON，字段规则不同。

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 本节重点 | 见官方文档 | — | — |

## 读代码

配置文件 pyproject.toml 用 TOML；读工具链文档时对照 tomllib 解析结果。

## 练习

```python exercise id=s14-l03-csv
# --- starter ---
row = ['y']
# --- solution ---
import csv
from io import StringIO
buf = StringIO('x\n1\n')
row = next(csv.reader(buf))
# --- check ---
assert row == ['x']
```

## 小结

- csv 处理行与分隔符
- tomllib 只读（3.11+）

## 延伸阅读

- [csv](https://docs.python.org/zh-cn/3/library/csv.html)
- [tomllib](https://docs.python.org/zh-cn/3/library/tomllib.html)
