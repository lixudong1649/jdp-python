#!/usr/bin/env python3
"""生成 Goal v2 阶段 12–24 课程 Markdown（可重复运行，覆盖同名文件）。"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parent.parent
COURSE = ROOT / "docs" / "课程"

DATE = "2026-10-18"


def lesson(
    *,
    stage: int,
    stage_slug: str,
    stage_short: str,
    num: int,
    slug: str,
    title: str,
    prereq: str,
    official: str,
    goals: list[str],
    concept: str,
    pitfalls: str,
    compare: str,
    read_code: str,
    ex_id: str,
    starter: str,
    solution: str,
    check: str,
    summary: list[str],
    links: list[str],
    pitfall_run: str = "",
) -> str:
    goals_md = "\n".join(f"- {g}" for g in goals)
    summary_md = "\n".join(f"- {s}" for s in summary)
    links_md = "\n".join(f"- {l}" for l in links)
    pitfall_block = pitfalls
    if pitfall_run:
        if "|||" in pitfall_run:
            code, exc = pitfall_run.split("|||", 1)
            fence = f"```python run raises={exc.strip()}\n"
        else:
            code, fence = pitfall_run, "```python run\n"
        pitfall_block += f"\n\n{fence}{code.strip()}\n```\n"
    return f"""---
title: {stage}.{num} {title}
---

# {stage}.{num} {title}

> 前置：{prereq} · 约 25 分钟 · 官方对应：{official}

## 目标

{goals_md}

## 核心概念

{concept}

## 易错点

{pitfall_block}

## 对照

{compare}

## 读代码

{read_code}

## 练习

```python exercise id={ex_id}
# --- starter ---
{starter.strip()}
# --- solution ---
{solution.strip()}
# --- check ---
{check.strip()}
```

## 小结

{summary_md}

## 延伸阅读

{links_md}
"""


STAGES: list[dict] = [
    {
        "no": 12,
        "slug": "12-数据模型与协议",
        "short": "数据模型与协议",
        "layer": "L2",
        "goal": "能写出支持 len/for/with 的自定义容器类",
        "project": "examples/项目/12-自定义容器类/ring_buffer.py",
        "lessons": [
            dict(
                slug="01-特殊方法全景",
                title="特殊方法全景",
                prereq="7.2 继承与特殊方法",
                official="[数据模型](https://docs.python.org/zh-cn/3/reference/datamodel.html#special-method-names)",
                goals=[
                    "列出常见特殊方法及其对应的内置语法",
                    "实现 `__repr__` 与 `__eq__` 便于调试与比较",
                    "理解特殊方法由解释器自动调用，不要手动加括号当普通方法",
                ],
                concept="""特殊方法（dunder）让对象参与内置操作：

```python run
class Point:
    def __init__(self, x: int, y: int) -> None:
        self.x, self.y = x, y

    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

p = Point(1, 2)
print(p, p == Point(1, 2))
```""",
                pitfalls="- 只写 `__eq__` 不写 `__hash__` 时实例默认不可哈希。\n- `__repr__` 必须返回 str，否则 `TypeError`。",
                pitfall_run="class Bad:\n    def __repr__(self):\n        return 123\n\nprint(repr(Bad()))|||TypeError",
                compare="| 概念 | Python | JS | Java |\n|---|---|---|---|\n| 字符串表示 | `__repr__` | 无标准 | `toString()` |\n| 相等 | `__eq__` | `===` | `equals()` |",
                read_code="SDK 模型类依赖 `__repr__` 让 `print(resp)` 可读；读代码时看到 `repr(x)` 或日志里的对象，想到类里是否实现了 `__repr__`。",
                ex_id="s12-l01-repr",
                starter="class Tag:\n    def __init__(self, name):\n        self.name = name",
                solution="class Tag:\n    def __init__(self, name):\n        self.name = name\n\n    def __repr__(self):\n        return f\"Tag(name={self.name!r})\"",
                check='t = Tag("py")\nassert repr(t) == "Tag(name=\'py\')"',
                summary=["特殊方法连接对象与内置语法", "`__repr__` 面向开发者调试", "`__eq__` 定义值相等"],
                links=[
                    "[特殊方法名称](https://docs.python.org/zh-cn/3/reference/datamodel.html#special-method-names)",
                ],
            ),
            dict(
                slug="02-迭代协议",
                title="迭代协议",
                prereq="10.1 迭代器与生成器",
                official="[迭代器协议](https://docs.python.org/zh-cn/3/c-api/iter.html)",
                goals=["实现 `__iter__`/`__next__` 或委托给内部容器", "让类支持 `for` 与 `iter()`", "区分可迭代对象与迭代器"],
                concept="""容器类通常实现 `__iter__` 返回迭代器：

```python run
class Countdown:
    def __init__(self, start: int) -> None:
        self.start = start

    def __iter__(self):
        n = self.start
        while n > 0:
            yield n
            n -= 1

print(list(Countdown(3)))
```""",
                pitfalls="- 只实现 `__getitem__` 不能自动支持 `for`（除非配合 `collections.abc.Sequence`）。\n- 迭代器耗尽后需重新创建。",
                compare="| | Python | JS | Java |\n|---|---|---|---|\n| 协议 | `__iter__` | `Symbol.iterator` | `Iterable` |",
                read_code="`for block in resp.content` 依赖 content 是可迭代对象；读 SDK 时查返回类型是否实现了序列或自定义迭代。",
                ex_id="s12-l02-iter",
                starter="class Two:\n    def __init__(self, a, b):\n        self.a, self.b = a, b",
                solution="class Two:\n    def __init__(self, a, b):\n        self.a, self.b = a, b\n\n    def __iter__(self):\n        yield self.a\n        yield self.b",
                check="assert list(Two(1, 2)) == [1, 2]",
                summary=["`for` 调用 iter/ next 协议", "生成器函数是简洁的 `__iter__` 实现"],
                links=["[类作为迭代器](https://docs.python.org/zh-cn/3/tutorial/classes.html#iterators)"],
            ),
            dict(
                slug="03-property与描述符入门",
                title="property 与描述符入门",
                prereq="7.2 继承与特殊方法",
                official="[property](https://docs.python.org/zh-cn/3/library/functions.html#property)",
                goals=["用 `@property` 把方法暴露成只读属性", "知道描述符是 `@property` 的底层机制（了解即可）"],
                concept="""```python run
class User:
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        return self._name

u = User("Ada")
print(u.name)
```""",
                pitfalls="- 对 property 加括号会 `TypeError`。\n- setter 里忘记校验会导致脏数据。",
                compare="| | Python | JS | Java |\n|---|---|---|---|\n| 访问器 | `@property` | `get x()` | getter 方法 |",
                read_code="Pydantic/FastAPI 模型属性看似字段，底层可能是描述符或 dataclass 生成；读代码时仍按“属性访问”理解。",
                ex_id="s12-l03-prop",
                starter="class Box:\n    def __init__(self, w):\n        self._w = w",
                solution="class Box:\n    def __init__(self, w):\n        self._w = w\n\n    @property\n    def w(self):\n        return self._w",
                check="b = Box(3)\nassert b.w == 3",
                summary=["property 延迟计算或封装", "读属性时不加括号"],
                links=["[描述符 HOWTO](https://docs.python.org/zh-cn/3/howto/descriptor.html)"],
            ),
            dict(
                slug="04-ABC与Protocol",
                title="ABC 与 Protocol",
                prereq="9.2 typing 进阶",
                official="[abc 模块](https://docs.python.org/zh-cn/3/library/abc.html)",
                goals=["用 ABC 声明必须实现的方法", "用 `typing.Protocol` 做结构化子类型（3.8 起稳定）"],
                concept="""```python run
from typing import Protocol

class SupportsLen(Protocol):
    def __len__(self) -> int: ...

def report_size(obj: SupportsLen) -> int:
    return len(obj)

print(report_size([1, 2, 3]))
```""",
                pitfalls="- ABC 子类未实现抽象方法无法实例化。\n- Protocol 只在类型检查时生效，运行时不强制。",
                compare="| | Python | JS | Java |\n|---|---|---|---|\n| 接口 | Protocol / ABC | TS interface | interface |",
                read_code="读 SDK 时常见 `Protocol` 或抽象基类约束客户端实现；静态类型帮助，运行时仍靠 duck typing。",
                ex_id="s12-l04-proto",
                starter="from typing import Protocol\n\nclass Runner(Protocol):\n    def run(self) -> str: ...",
                solution="from typing import Protocol\n\nclass Runner(Protocol):\n    def run(self) -> str: ...\n\nclass Job:\n    def run(self) -> str:\n        return \"ok\"\n\ndef go(r: Runner) -> str:\n    return r.run()",
                check='assert go(Job()) == "ok"',
                summary=["Protocol 描述能力而非继承", "ABC 适合强制子类实现"],
                links=[
                    "[typing.Protocol](https://docs.python.org/zh-cn/3/library/typing.html#typing.Protocol)",
                    "[abc](https://docs.python.org/zh-cn/3/library/abc.html)",
                ],
            ),
        ],
    },
]

from bootstrap_v2_courses_data import EXTRA_STAGES

STAGES.extend(EXTRA_STAGES)


def write_stage(stage: dict) -> None:
    d = COURSE / stage["slug"]
    d.mkdir(parents=True, exist_ok=True)
    rows = []
    for i, les in enumerate(stage["lessons"], 1):
        fname = les["slug"] if re.match(r"^\d\d-", les["slug"]) else f"{i:02d}-{les['slug']}"
        path = d / f"{fname}.md"
        body = lesson(
            stage=stage["no"],
            stage_slug=stage["slug"],
            stage_short=stage["short"],
            num=i,
            slug=les["slug"],
            title=les["title"],
            prereq=les["prereq"],
            official=les["official"],
            goals=les["goals"],
            concept=les["concept"],
            pitfalls=les["pitfalls"],
            compare=les["compare"],
            read_code=les["read_code"],
            ex_id=les["ex_id"],
            starter=les["starter"],
            solution=les["solution"],
            check=les["check"],
            summary=les["summary"],
            links=les["links"],
            pitfall_run=les.get("pitfall_run", ""),
        )
        path.write_text(body, encoding="utf-8")
        rows.append(f"| [{stage['no']}.{i} {les['title']}]({fname}.md) | {les['goals'][0]} |")
    idx = d / "index.md"
    table = "\n".join(rows)
    proj = stage.get("project", "")
    proj_line = f"\n阶段项目：[`{proj}`](../../../{proj})（含 pytest）。" if proj else ""
    idx.write_text(
        f"""---
title: 阶段 {stage['no']} · {stage['short']}
goal: {stage['goal']}
layer: {stage['layer']}
---

# 阶段 {stage['no']} · {stage['short']}

**达成标志**：{stage['goal']}。{proj_line}

| 课程 | 你将学会 |
|---|---|
{table}

前置：完成 v1 阶段 1–11；本阶段属 **{stage['layer']}**（核对日期 {DATE}，正文对 Python 3.12–3.15 成立，项目固定 3.12）。
""",
        encoding="utf-8",
    )


def main() -> None:
    for st in STAGES:
        write_stage(st)
    print(f"Wrote {len(STAGES)} stages under {COURSE}")


if __name__ == "__main__":
    main()
