"""从日志行统计级别计数（阶段 14 项目）。"""
from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

LEVEL_RE = re.compile(r"\b(INFO|WARNING|ERROR|DEBUG)\b")


def parse_lines(text: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for line in text.splitlines():
        m = LEVEL_RE.search(line)
        if m:
            counts[m.group(1)] += 1
    return counts


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="统计日志级别出现次数")
    p.add_argument("file", type=Path, help="日志文件路径")
    args = p.parse_args(argv)
    text = args.file.read_text(encoding="utf-8")
    counts = parse_lines(text)
    for level in ("DEBUG", "INFO", "WARNING", "ERROR"):
        if counts[level]:
            print(f"{level}: {counts[level]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
