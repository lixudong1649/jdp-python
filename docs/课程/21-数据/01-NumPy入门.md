---
title: 21.1 NumPy 入门
---

# 21.1 NumPy 入门

> 前置：2.2 数字与运算、14.3 csv · 约 35 分钟 · 官方对应：[NumPy 用户指南](https://numpy.org/doc/stable/user/index.html) · 核对日期 2026-10-18（课程环境 Python 3.12；NumPy 2.x 经 `uv sync --group data` 安装）

## 目标

- 理解 **ndarray**：同质、定长、带 `dtype` 的连续存储，与 Python `list` 的“装任意对象”不同。
- 会用向量化运算替代手写 `for` 循环做逐元素算术（本地 NumPy 示例见静态块；课内可运行块用纯 Python 对照）。
- 知道 **广播（broadcasting）** 让形状不同的数组在规则下对齐运算，以及常见踩坑。
- 能把 NumPy 当作阶段 21 项目 `analyze.py` 的前置：列数据最终可升级为 `ndarray` 做统计。
- 能在本地用 `uv sync --group data` 安装与课文一致的 NumPy 2.x 栈。

## 核心概念

### ndarray 与 dtype

NumPy 数组要求元素类型一致（`int64`、`float64` 等），在 C 层连续存放，因此 `a + b` 可以在一次循环里完成，而不是 Python 层对每个元素 dispatch。

```python
import numpy as np

a = np.array([1, 2, 3], dtype=np.int64)
b = np.array([4, 5, 6], dtype=np.int64)
print(a.shape, a.dtype)
print(a + b)          # [5 6 7]，无 Python 层 zip
print((a * 2).tolist())
```

本地验证：先 `uv sync --group data`，再在项目根执行 `uv run python -c "import numpy as np; print(np.__version__)"`。

### 形状与 reshape

`shape` 描述各维长度；`reshape` 改变视图形状（元素总数不变）。读别人代码时先看 `shape` 再猜广播结果。

```python
import numpy as np

grid = np.arange(6).reshape(2, 3)
print(grid)
print(grid.sum(axis=0))   # 按列求和 → shape (3,)
print(grid.sum(axis=1))   # 按行求和 → shape (2,)
```

### 课内可运行：用 list 模拟“向量化”

浏览器课内没有 NumPy wheel；下面用列表推导对照“一次表达式处理整列”的思路，与 `ndarray` 运算语义类似。

```python run
a = [1.0, 2.0, 3.0]
b = [4.0, 5.0, 6.0]
vec = [x + y for x, y in zip(a, b)]
scaled = [x * 2 for x in vec]
print(vec, scaled)
```

### 聚合与布尔索引

统计列均值、按条件筛选行，是 CSV 报告的常见下一步（阶段项目先用 `statistics.mean`，逻辑相同）。

```python
import numpy as np

temps = np.array([22.0, 18.0, 25.0, 18.0])
print(temps.mean(), temps.std())
mask = temps >= 20
print(temps[mask])
```

### 广播示意

```python
import numpy as np

base = np.array([[1, 2, 3], [4, 5, 6]])
offset = np.array([10, 20, 30])   # (3,) 广播到每一行
print(base + offset)
```


## 易错点

- **把 `np.array` 当 list 用**：`a.append` 不存在；要增长用 `np.concatenate` 或先 list 再转数组。
- **dtype 意外**：`np.array([1, 2, 3]) / 2` 在整数 dtype 上会截断；分析温度应显式 `dtype=float64`。
- **广播形状不兼容**会 `ValueError`；先打印 `a.shape, b.shape`。

```python run raises=ValueError
a = [1, 2]
b = [1, 2, 3]
# 纯 Python 没有广播；zip 长度不同会在这里暴露问题
_ = [x + y for x, y in zip(a, b, strict=True)]
```

- **视图与副本**：切片常是视图，原地修改会影响原数组；需要独立副本用 `.copy()`。

课内再练一列统计：与 `avg_column` 相同公式，用纯 Python 验证测试期望值。

```python run
from statistics import mean

temps = [22.0, 18.0]
print(mean(temps))
```

## 对照

| 概念 | Python + NumPy | JavaScript | Java |
|---|---|---|---|
| 同质数值数组 | `numpy.ndarray` + `dtype` | `Float64Array` 等 TypedArray | `double[]` / 多维数组 |
| 逐元素运算 | `a + b` 向量化 | 需循环或库 | 循环或 `Arrays` 工具 |
| 二维表统计 | `axis=0/1` 聚合 | 常借助库或手写 | 流/循环或 ND4J 等 |
| 课内运行 | 静态块 + 本地 `uv run` | Pyodide 无 NumPy | 同左 |

## 读代码

阶段 21 项目 [`examples/项目/21-CSV分析报告/analyze.py`](../../../examples/项目/21-CSV分析报告/analyze.py) 用标准库读 CSV 并算列均值；读懂它等于读懂“列 → 浮点列表 → 聚合”管线，换成 NumPy 只需把 `values` 换成 `np.asarray(values)`。

```python
"""CSV 列聚合（阶段 21，仅用标准库 + pandas 在测试中可选）。"""
from __future__ import annotations

import csv
from io import StringIO
from statistics import mean


def avg_column(csv_text: str, column: str) -> float:
    reader = csv.DictReader(StringIO(csv_text))
    values = [float(row[column]) for row in reader]
    return mean(values)
```

逐行说明：

1. `StringIO(csv_text)` 让内存字符串像文件一样喂给 `DictReader`，测试不必写临时文件。
2. `DictReader` 首行作表头，每行是 `dict`，键名即列名（与 14.3 课一致）。
3. `float(row[column])` 显式转型：CSV 读出来全是 `str`，和 NumPy 里指定 `dtype` 同理。
4. `mean(values)` 与 `np.mean(values)` 在数学上一致；大表时 ndarray 更省内存、更快。
5. 若列名拼错，会在 `row[column]` 处 `KeyError`；测试用例应覆盖正常与缺列。
6. 函数签名 `column: str` 让类型检查器在传错类型时告警；与 pandas `df["temp"]` 的列名字符串一致。
7. 未来若接入 NumPy，可把 `values` 换成 `np.asarray(values, dtype=float64)` 再 `values.mean()`，接口可保持不变。

运行与测试（项目根目录）：

```bash
uv sync --group data
uv run pytest examples/项目/21-CSV分析报告/test_analyze.py -q
```

期望：`1 passed`；`test_avg_column` 对 `temp` 列断言均值为 `20.0`。

## 练习

### 练习 1：列表向量加法

```python exercise id=s21-l01-np
# --- starter ---
def vec_add(a: list[float], b: list[float]) -> list[float]:
    return []
# --- solution ---
def vec_add(a: list[float], b: list[float]) -> list[float]:
    return [x + y for x, y in zip(a, b, strict=True)]
# --- check ---
assert vec_add([1.0, 2.0], [3.0, 4.0]) == [4.0, 6.0]
```

### 练习 2：列均值（标准库版）

实现 `column_mean(rows: list[dict[str, str]], key: str) -> float`：从 `DictReader` 风格的行字典列表取出 `key` 列转 float 后求均值。

```python exercise id=s21-l01-mean
# --- starter ---
def column_mean(rows: list[dict[str, str]], key: str) -> float:
    return 0.0
# --- solution ---
def column_mean(rows: list[dict[str, str]], key: str) -> float:
    vals = [float(r[key]) for r in rows]
    return sum(vals) / len(vals)
# --- check ---
rows = [{"temp": "22"}, {"temp": "18"}]
assert column_mean(rows, "temp") == 20.0
```

### 与阶段 21 项目的衔接

`avg_column` 当前只用 `statistics.mean`；你在本地可用 NumPy 写等价实现并对比性能（大文件时 ndarray 更占优）。无论哪条路径，**测试字符串**保持不变，保证 CI 不依赖随机数据文件。提交前务必在项目根执行 `uv run pytest examples/项目/21-CSV分析报告/test_analyze.py -q`，确认与课文引用的命令一致。

读 ndarray 打印结果时，`array([1,2,3])` 与 `list` 的 `repr` 不同，便于一眼区分类型。

学习 NumPy 时建议手抄一张小抄：`shape`、`dtype`、`axis` 三个词分别问“多大”“什么类型”“沿哪根轴聚合”。遇到报错先把数组 `print(repr(a))` 打出来，比盲改广播规则更快。


## 小结

- ndarray 提供同质存储与向量化运算；分析数值列时优先想清楚 `dtype` 与 `shape`。
- 课内用静态 NumPy 块 + 本地 `uv sync --group data` 运行；可运行块用 list 对照语义。
- 广播能减少显式循环，但形状不匹配会立刻报错，调试时先打印 `shape`。
- 阶段项目 `avg_column` 是 NumPy/pandas 路线的最小标准库版本，测试命令见上文。
- `np.save` / `np.load` 适合中间结果缓存，CSV 仍是最通用交换格式。
- 随机数用 `np.random.default_rng`（Generator API），旧 `np.random.seed` 全局状态少用。
- 线性代数在 `np.linalg`，本阶段只需知道存在即可。
- 与 pandas 互转：`df.values` 或 `df.to_numpy()` 得 ndarray。
- 布尔索引返回副本还是视图依索引类型而定，赋值前用 `.copy()` 更稳。
- 课内静态块请在本地执行，浏览器站点不加载 NumPy wheel。
- 遇到 `NaN` 用 `np.isnan` 过滤，聚合前清洗数据。

## 延伸阅读

- [NumPy 快速入门](https://numpy.org/doc/stable/user/quickstart.html)
- [NumPy 广播规则](https://numpy.org/doc/stable/user/basics.broadcasting.html)
