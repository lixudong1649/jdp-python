"""CSV 列聚合（阶段 21，仅用标准库 + pandas 在测试中可选）。"""
from __future__ import annotations

import csv
from io import StringIO
from statistics import mean


def avg_column(csv_text: str, column: str) -> float:
    reader = csv.DictReader(StringIO(csv_text))
    values = [float(row[column]) for row in reader]
    return mean(values)
