import re
from collections import Counter
from pathlib import Path

LEVEL_RE = re.compile(r"\b(INFO|ERROR)\b")


def count_levels(text: str) -> Counter[str]:
    c: Counter[str] = Counter()
    for line in text.splitlines():
        m = LEVEL_RE.search(line)
        if m:
            c[m.group(1)] += 1
    return c


def main(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    for level, n in sorted(count_levels(text).items()):
        print(f"{level}: {n}")
    return 0
