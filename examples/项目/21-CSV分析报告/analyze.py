"""CSV 列聚合与简单统计报告（阶段 21：csv + statistics + CLI）。"""
from __future__ import annotations

import argparse
import csv
import sys
from io import StringIO
from pathlib import Path
from statistics import mean, pstdev


class AnalyzeError(ValueError):
    """CSV 解析或列统计失败。"""


def _read_numeric_column(csv_text: str, column: str) -> list[float]:
    if not column.strip():
        raise AnalyzeError("列名不能为空")
    reader = csv.DictReader(StringIO(csv_text))
    if reader.fieldnames is None or column not in reader.fieldnames:
        raise AnalyzeError(f"缺少列: {column}")
    values: list[float] = []
    for row in reader:
        raw = row.get(column, "").strip()
        if not raw:
            continue
        try:
            values.append(float(raw))
        except ValueError as e:
            raise AnalyzeError(f"列 {column} 含非数字: {raw!r}") from e
    if not values:
        raise AnalyzeError(f"列 {column} 没有可用数值")
    return values


def avg_column(csv_text: str, column: str) -> float:
    return mean(_read_numeric_column(csv_text, column))


def column_stats(csv_text: str, column: str) -> dict[str, float]:
    values = _read_numeric_column(csv_text, column)
    spread = pstdev(values) if len(values) > 1 else 0.0
    return {
        "count": float(len(values)),
        "mean": mean(values),
        "min": min(values),
        "max": max(values),
        "stdev": spread,
    }


def format_report(stats: dict[str, float], column: str) -> str:
    lines = [
        f"列: {column}",
        f"  count: {int(stats['count'])}",
        f"  mean:  {stats['mean']:.2f}",
        f"  min:   {stats['min']:.2f}",
        f"  max:   {stats['max']:.2f}",
        f"  stdev: {stats['stdev']:.2f}",
    ]
    return "\n".join(lines)


def load_csv_text(path: Path) -> str:
    if not path.is_file():
        raise AnalyzeError(f"文件不存在: {path}")
    return path.read_text(encoding="utf-8")


def analyze_text(csv_text: str, column: str) -> str:
    stats = column_stats(csv_text, column)
    return format_report(stats, column)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CSV 数值列统计报告")
    parser.add_argument("file", type=Path, help="CSV 文件路径")
    parser.add_argument("column", help="要统计的列名")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        text = load_csv_text(args.file)
        print(analyze_text(text, args.column))
    except AnalyzeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
