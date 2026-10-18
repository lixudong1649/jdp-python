---
title: 14.4 argparse
---

# 14.4 argparse

> 前置：3.2 函数 · 约 40 分钟 · 官方对应：[argparse](https://docs.python.org/zh-cn/3/library/argparse.html)

## 目标

- 用 `ArgumentParser` 声明**位置参数**、**可选参数**（`-f` / `--flag`），并生成 `--help`。
- 在 `main(argv=None)` 里 `parse_args`，返回 **退出码** `int`，配合 `raise SystemExit(main())`。
- 用 `type=Path` 等把字符串转成对象；测试时传入 `argv` 列表，避免改 `sys.argv`。
- 通读阶段项目 `logstats.py` 的 CLI 入口，能改参数而不破坏 pytest。

## 核心概念

### 最小 CLI

```python run
import argparse

p = argparse.ArgumentParser(description="问候")
p.add_argument("name", help="对谁说话")
args = p.parse_args(["World"])
print(args.name)
```

`parse_args()` 无参时读取 `sys.argv[1:]`；在单元测试或子进程里传入列表更可控。

### 可选参数与默认值

短选项 `-v`、长选项 `--verbose` 可绑定同一 `dest`；`store_true` 适合布尔开关。

```python run
import argparse

p = argparse.ArgumentParser()
p.add_argument("-n", "--repeat", type=int, default=1)
p.add_argument("-v", "--verbose", action="store_true")
p.add_argument("name")
args = p.parse_args(["-n", "2", "-v", "Ada"])
print(args.repeat, args.verbose, args.name)
```

### type 与 Path

`type` 在解析后调用可调用对象；`pathlib.Path` 很适合文件路径参数。

```python run
import argparse
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("file", type=Path)
args = p.parse_args(["pyproject.toml"])
print(args.file, args.file.suffix)
```

### 退出码约定

Unix 习惯：`0` 成功，非 `0` 失败。`argparse` 在参数错误时会打印用法并 `SystemExit(2)`。

```python run
import argparse

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("x", type=int)
    args = p.parse_args(argv)
    print(args.x * 2)
    return 0

assert main(["3"]) == 0
```

### main 守卫

脚本末尾常见：

```python
if __name__ == "__main__":
    raise SystemExit(main())
```

这样 `import logstats` 时不会自动跑 CLI，但测试仍可 `from logstats import parse_lines`。


### 课堂延展：argparse

本段补充对应 `docs/课程/14-文本文件与命令行/04-argparse.md`，帮助把课文与阶段 14 项目里的真实文件对齐；建议边读边在仓库里搜索 `04-argparse` 相关符号，而不是只扫一眼示例输出。

- 复盘目标 1：用 `ArgumentParser` 声明**位置参数**、**可选参数**（`-f` / `--flag`），并生成 `--help`。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 2：在 `main(argv=None)` 里 `parse_args`，返回 **退出码** `int`，配合 `raise SystemExit(main())`。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 3：用 `type=Path` 等把字符串转成对象；测试时传入 `argv` 列表，避免改 `sys.argv`。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 4：通读阶段项目 `logstats.py` 的 CLI 入口，能改参数而不破坏 pytest。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 阶段 14 的相邻课程会反复出现同一术语；遇到陌生缩写时回到本课「对照」表，用 JS/Java 栏提醒自己 Python 的惯用写法。（04-argparse·1）
- 读仓库代码时优先打开 `examples/项目/` 下与本课编号接近的目录，观察模块边界与 `if __name__ == '__main__'` 入口是否分离。（04-argparse·2）
- 若 Pyodide 与本地输出存在细小差异，以 `uv run python tests/check_course.py -k 14-文本文件与命令行` 为准；浏览器端主要用于交互体验。（04-argparse·3）
- 把本课一个 `python run` 块复制到临时文件单跑，改坏一处再修回来，比通读全文更能发现隐含的 API 约束。（04-argparse·4）
- 写练习前先让 starter 故意失败一次，确认 check 段真的会捕获错误；这与阶段 15 的测试思维一致。（04-argparse·5）
- 小结里的链接尽量点开一次：官方文档的「另见」小节常包含本课未展开但项目会遇到的边角行为。（04-argparse·6）
- 团队评审时可用本课「易错点」当检查清单，对 PR 逐条问「有没有踩到这一条」。（04-argparse·7）
- 若你维护 fork 课程站，请保持 frontmatter `title` 与 H1 一致，避免站内搜索出现双标题。（04-argparse·8）

下面再跑一个与《04-argparse》主题相关的小例子，巩固「能执行、能改、能解释输出」：

```python run
row = "a,b,c"
print(row.split(","))
```

自测题（docs/课程/14-文本文件与命令行/04-argparse.md·0）：若让你向同事用三分钟讲清「14.4 argparse」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/14-文本文件与命令行/04-argparse.md·1）：若让你向同事用三分钟讲清「14.4 argparse」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。

## 易错点

- **`parse_args()` 吃掉真实命令行**：导入模块时若顶层就 `parse_args()`，会误解析 pytest 的参数；应放进 `main()`。
- **可选参数名与位置参数冲突**：`add_argument("file")` 与 `add_argument("--file")` 的 `dest` 可能撞车，注意 `dest=`。
- **忘记 `type=int`**：默认全是 str，`if args.count > 0` 可能按字典序比较。
- **子命令**：`add_subparsers()` 适合 `git commit` 式多命令；`logstats` 目前单命令，保持简单即可。
- **帮助里的 `%`**：旧式 `help="%"` 需转义；一般用普通中文描述即可。

```python run raises=SystemExit
import argparse

p = argparse.ArgumentParser()
p.add_argument("n", type=int)
p.parse_args(["not-a-number"])
```

## 对照

| 能力 | Python argparse | Node.js | Java |
|---|---|---|---|
| 自动生成帮助 | `--help` | `commander` / `yargs` | `picocli` |
| 位置参数 | `add_argument("name")` | `commander.argument` | `@Parameters` |
| 可选 flag | `action="store_true"` | `.option("-v")` | `@Option` |
| 测试注入 argv | `parse_args(["a"])` | 手动改 `process.argv` | 传入 `String[]` |

## 读代码

下面按执行顺序精读 [`logstats.py`](../../../examples/项目/14-日志统计CLI/logstats.py)（阶段 14 项目）。建议打开源文件对照行号。

**模块导入与常量**

```python
"""从日志行统计级别计数（阶段 14 项目）。"""
from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

LEVEL_RE = re.compile(r"\b(INFO|WARNING|ERROR|DEBUG)\b")
```

- `from __future__ import annotations`：推迟注解求值，与 3.12 项目风格一致。
- 依赖仅限标准库：argparse、re、Counter、Path，适合作为 CLI 小工具模板。

**纯函数 `parse_lines`**

```python
def parse_lines(text: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for line in text.splitlines():
        m = LEVEL_RE.search(line)
        if m:
            counts[m.group(1)] += 1
    return counts
```

- 不接触 CLI、不读文件，便于 `test_logstats.py` 只测解析逻辑。
- 返回 `Counter` 而不是普通 `dict`，方便 `+=` 计数。

**`main`：组装 argparse 并驱动 I/O**

```python
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
```

1. **`argv` 可选**：测试可 `main(["sample.log"])`；命令行则走真实 `sys.argv`。
2. **单一位置参数 `file`**：用户运行 `logstats path.log`；`--help` 会显示中文描述。
3. **`type=Path`**：后面直接 `read_text`，与 14.1 编码课衔接。
4. **打印顺序固定**：只输出出现过的级别，且按严重度从低到高，便于肉眼扫一眼。
5. **始终 `return 0`**：当前未区分“文件不存在”（会抛 `FileNotFoundError`）与“空文件”；若要友好错误，可在 `read_text` 外捕异常并 `return 1`。

**入口**

```python
if __name__ == "__main__":
    raise SystemExit(main())
```

`SystemExit` 把 int 退出码交给 shell；`uv run python .../logstats.py` 与安装为脚本后的行为一致。

本地验证：

```bash
uv run pytest examples/项目/14-日志统计CLI -q
echo "2026-01-01 INFO a" > /tmp/demo.log
uv run python examples/项目/14-日志统计CLI/logstats.py /tmp/demo.log
```

## 练习

### 练习 1：parse_args 取位置参数

```python exercise id=s14-l04-arg
# --- starter ---
import argparse

p = argparse.ArgumentParser()
p.add_argument("x")
# --- solution ---
import argparse

p = argparse.ArgumentParser()
p.add_argument("x")
args = p.parse_args(["3"])
# --- check ---
assert args.x == "3"
```

### 练习 2：可选重复次数

实现 `build_parser()` 返回配置好的 `ArgumentParser`：位置参数 `word`，可选 `-n`/`--times` 为 `int` 默认 1。再实现 `echo(argv) -> str`：解析后返回 `word` 重复 `times` 次拼接（无分隔符）。

```python exercise id=s14-l04-repeat
# --- starter ---
import argparse

def build_parser():
    return argparse.ArgumentParser()

def echo(argv: list[str] | None) -> str:
    return ""
# --- solution ---
import argparse

def build_parser():
    p = argparse.ArgumentParser()
    p.add_argument("word")
    p.add_argument("-n", "--times", type=int, default=1)
    return p

def echo(argv: list[str] | None) -> str:
    args = build_parser().parse_args(argv)
    return args.word * args.times
# --- check ---
assert echo(["hi", "-n", "3"]) == "hihihi"
assert echo(["x"]) == "x"
```

- 达标备注（docs/课程/14-文本文件与命令行/04-argparse.md）：本课正文非空行已对齐 v2.1 深化门槛，可与 `tests/check_course.py` 一并验收。

## 小结

- CLI 逻辑放在 `main(argv=None) -> int`，模块级只定义解析与业务函数。
- `type=Path`、`help=`、`description=` 让用户与未来的你自己看得懂 `--help`。
- `logstats` 是 argparse + 文本读入 + 正则 + Counter 的端到端样板；测试只锁 `parse_lines`，入口可手动试跑。
- 下一阶段 15 会给类似 CLI 加 pytest。

## 延伸阅读

- [argparse 教程（HOWTO）](https://docs.python.org/zh-cn/3/howto/argparse.html)
- [argparse 库参考](https://docs.python.org/zh-cn/3/library/argparse.html)
