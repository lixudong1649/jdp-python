---
title: 21.3 Jupyter 工作流
---

# 21.3 Jupyter 工作流

> 前置：21.2 pandas · 约 30 分钟 · 官方对应：[JupyterLab 文档](https://jupyter.org/documentation) · 核对日期 2026-10-18

## 目标

- 知道 **Jupyter Notebook / JupyterLab** 适合探索性数据分析：逐格运行、立刻看图与表。
- 区分 **探索笔记本** 与 **可交付模块**：最终逻辑应落到 `.py` + `pytest`，与本仓库 Markdown 课 + 阶段项目一致。
- 会用“自上而下”阅读他人 notebook：先看 import 与数据路径，再找清洗与结论单元。
- 把 notebook 与阶段 21 项目衔接：在本地试 pandas，再把稳定函数迁入 `analyze.py` 并跑测试。
- 能说明为何本仓库主课用 Markdown 而非 notebook 入库。

## 核心概念

### Notebook 单元格模型

每个代码单元在上次内核状态下执行；变量在单元格之间共享，因此**执行顺序**不等于文件从上到下的视觉顺序。

```python run
state = {"step": 0}

def run_cell(code: str) -> None:
    exec(code, state)

run_cell("step = step + 1")
run_cell("step = step + 1")
print(state["step"])
```

### 从探索到脚本

探索时常用临时变量名；提交前应提取函数、加类型注解，并写入测试。

```python run
RAW = "city,temp\n上海,22\n北京,18\n"

def preview_rows(text: str, n: int = 5) -> list[str]:
    lines = text.strip().splitlines()[:n]
    return lines

print(preview_rows(RAW))
```

### 与 pandas 静态示例对照

本地 notebook 里可粘贴 21.2 的 `read_csv` 块；课内不执行 pandas，只展示典型单元：

```python
# 典型探索单元（本地 Jupyter 运行）
import pandas as pd
from pathlib import Path

path = Path("examples/项目/21-CSV分析报告/sample.csv")  # 若自建样例
# df = pd.read_csv(path)
# df.head()
```

本仓库阶段项目不强制 sample 文件，测试用内存字符串；notebook 可用 `StringIO` 与测试保持一致。

### 输出与 `%matplotlib`

绘图单元常在 notebook 里 `%matplotlib inline`；交付 CLI 则改为 `savefig` 或把图写入报告目录。课内演示“累积文本输出”：

```python run
chunks = ["图1: ", "柱状", " ", "完成\n"]
report = []
for c in chunks:
    report.append(c)
print("".join(report))
```

### 版本与内核

Jupyter 内核版本必须与本项目 `requires-python >= 3.12` 一致；核对日期 2026-10-18 时官方最新稳定为 3.15，本仓锁定 3.12。notebook 元数据里的 `kernelspec` 应指向 3.12，避免 `tomllib` / 类型语法差异。


## 易错点

- **乱序执行**：先跑下面单元再跑上面，变量可能是旧的；重启内核 + Run All 再导出结果。
- **把大输出提交进 Git**：notebook JSON 里塞满 DataFrame 打印会膨胀 diff；清理输出再提交，或用 `nbstripout`。
- **密钥进 notebook**：与 `.env` 规则相同，API Key 不要写在单元格里。
- **只有 notebook 没有测试**：`analyze.py` 的存在就是为了可测；探索满意后复制函数体进模块。

```python run raises=RuntimeError
def must_fail():
    raise RuntimeError("模拟 notebook 里未捕获的异常")

must_fail()
```

## 对照

| 维度 | Jupyter | 本仓库 Markdown 课 | 传统 IDE |
|---|---|---|---|
| 运行单位 | 单元格 | 代码块（Pyodide / 本地） | 单文件 |
| 状态 | 内核常驻 | 每块独立子进程 | 调试会话 |
| 交付 | 需导出 .py | 已是文本 + 测试 | 直接模块 |
| Code Review | diff 噪声大 | Git 友好 | 友好 |

## 读代码

阶段 21 可交付代码仍是 [`analyze.py`](../../../examples/项目/21-CSV分析报告/analyze.py)。读 notebook 时若看到同样逻辑，应对照模块版是否多了边界检查：

```python
from __future__ import annotations

import csv
from io import StringIO
from statistics import mean


def avg_column(csv_text: str, column: str) -> float:
    reader = csv.DictReader(StringIO(csv_text))
    values = [float(row[column]) for row in reader]
    if not values:
        raise ValueError("empty column")
    return mean(values)
```

上面在 notebook 里可能少 `if not values`；迁入模块时应补上并加测试。运行回归：

```bash
uv sync --group data
uv run pytest examples/项目/21-CSV分析报告/test_analyze.py -q
```

Jupyter 本地启动（可选，不纳入 CI）：

```bash
uv sync --group data
uv run jupyter lab
```

若未安装 `jupyter`，仅安装 `data` 组不会带上；需要时 `uv add --group dev jupyter` 或按官方文档单独安装。课程验收以 pytest 为准。

把探索笔记导出为 `.py` 时，去掉魔法命令（`%matplotlib` 等），改为普通 import，以便 `ruff` 与 pytest 能静态分析。

## 练习

### 练习 1：模拟单元格顺序

```python exercise id=s21-l03-jup
# --- starter ---
def run_all(cells: list[str]) -> int:
    return 0
# --- solution ---
def run_all(cells: list[str]) -> int:
    env: dict[str, int] = {"x": 0}
    for code in cells:
        exec(code, env)
    return env["x"]
# --- check ---
cells = ["x = 1", "x = x + 2"]
assert run_all(cells) == 3
```

### 练习 2：提取预览函数

实现 `first_data_line(csv_text: str) -> str`：跳过表头，返回第一行数据（不含换行）。

```python exercise id=s21-l03-line
# --- starter ---
def first_data_line(csv_text: str) -> str:
    return ""
# --- solution ---
def first_data_line(csv_text: str) -> str:
    lines = csv_text.strip().splitlines()
    if len(lines) < 2:
        raise ValueError("no data")
    return lines[1]
# --- check ---
t = "city,temp\n上海,22\n北京,18\n"
assert first_data_line(t) == "上海,22"
```

### 协作与审查

Notebook 适合个人探索；团队合并时优先审查 `analyze.py` 与测试 diff。若必须用 notebook 演示，建议导出关键函数到模块后再开 PR，并在描述里贴上 `pytest` 输出截图或日志，避免“只有截图、无法复现”的交付物。

写 notebook 时给每个分析单元加一行 Markdown 说明“输入是什么、输出给谁看”，日后转脚本时这段文字可直接变成函数 docstring。内核重启后变量清空是特性不是 bug，养成 Run All 再保存的习惯。

对比 Colab 与本地 Jupyter：密钥与数据合规策略不同，企业数据优先本地或私有部署。


## 小结

- Jupyter 适合探索；本仓库用 Markdown + pytest 保证可重复验证。
- 读 notebook 先看内核版本与执行顺序；交付前把逻辑迁入 `.py` 并跑阶段测试。
- pandas/NumPy 在 notebook 里试用，在 `examples/项目/21-CSV分析报告` 里固化。
- 测试命令：`uv run pytest examples/项目/21-CSV分析报告/test_analyze.py -q`。

若 notebook 体积过大，可在本地用官方工具清理输出后再 `git add`，保持仓库 diff 可读。

- Notebook 元数据含内核名，换机器要重选内核。
- `%timeit` 魔法适合微基准，交付代码改用 `timeit` 模块。
- 图表单元输出体积大，清理后再提交 Git。
- 与 VS Code 内置 notebook 交互类似，概念可迁移。
- 阶段 21 以 pytest 为验收，notebook 不作 CI 输入。
- 探索用 `StringIO` 与测试共享同一 CSV 文本，减少漂移。
- 导出脚本后加 `if __name__ == "__main__"` 便于命令行复跑。
- Jupyter 单文件 `.ipynb` 是 JSON，合并冲突时优先改 `.py` 模块。
- 教课时用「重启内核 → Run All」作为提交前检查清单第一项。
- 把随机种子写在首个代码单元，保证探索可重复。
- 大表预览用 `df.head()` 而非 `print(df)`，notebook 输出更轻。
- 核对日期 2026-10-18：JupyterLab 4 界面与扩展生态以官方文档为准。
- 将 notebook 中验证过的 `avg_column` 逻辑与 `analyze.py` 逐行 diff，确保无漂移。

## 延伸阅读

- [JupyterLab 入门](https://jupyter.org/documentation)
