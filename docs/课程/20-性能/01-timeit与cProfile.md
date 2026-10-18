---
title: 20.1 timeit 与 cProfile
---

# 20.1 timeit 与 cProfile

> 前置：18. 并发 · 约 35 分钟 · 官方对应：[timeit](https://docs.python.org/zh-cn/3/library/timeit.html)、[profile](https://docs.python.org/zh-cn/3/library/profile.html) · 核对日期 2026-10-18（测量优先；课程 Python 3.12）

## 目标

- 用 `timeit` 对小段代码做 **重复计时**，理解 `number` 与噪声。
- 用 `cProfile` 找到 **热点函数** 与调用次数，而不是凭直觉猜瓶颈。
- 建立「先 profile 再优化」的习惯，并知道微基准的局限。
- 能把阶段 20 项目 `slow_math.py` 的两种实现放进对比实验。

## 核心概念

### timeit：重复执行取稳定读数

`timeit.timeit(stmt, number=N)` 执行 `stmt` 共 `N` 次，返回总秒数（不是单次）。适合比较 **相对快慢**，不适合只跑一次就下结论。

```python run
import timeit

t_list = timeit.timeit("sum(range(200))", number=50_000)
t_comp = timeit.timeit("sum(i for i in range(200))", number=50_000)
print(t_list > 0, t_comp > 0, t_list < t_comp * 3)
```

内置 `sum(range(...))` 通常更快；倍数关系随机器变化，**看趋势**即可。

### 比较两个可调用对象

对函数对象用 `timeit` 时，用 `lambda` 或 `stmt='f(n)'` 并传入 `globals`：

```python run
import timeit

def slow(n: int) -> int:
    return sum(i * i for i in range(n))

def fast(n: int) -> int:
    return n * (n - 1) * (2 * n - 1) // 6

n = 500
t_slow = timeit.timeit(lambda: slow(n), number=2000)
t_fast = timeit.timeit(lambda: fast(n), number=2000)
print(t_slow > t_fast, round(t_slow / max(t_fast, 1e-9), 1) >= 1.0)
```

当 `n` 较大时，`fast` 应明显更短；若差异不大，先增大 `n` 或 `number`。

### cProfile：谁被调用了多少次

`Profile().runcall(fn)` 在课内与 Pyodide 中比 `cProfile.run('fn()')` 更稳妥（后者在隔离命名空间易 `NameError`）。

```python run
import cProfile

def work(steps: int) -> int:
    total = 0
    for i in range(steps):
        total += i % 3
    return total

prof = cProfile.Profile()
result = prof.runcall(work, 5000)
stats = prof.getstats()
print(result >= 0, len(stats) >= 1)
```

读报告时关注 `ncalls`、`tottime`、`cumtime`；优化 **高 cumtime** 且可改动的纯 Python 循环。

### 测量流程建议

1. 用代表性输入（生产级数量级）。
2. `timeit` 粗比 → `cProfile` 定位函数 → 改算法或数据结构（20.2–20.3）。
3. 改完再测；只汇报前后数字，避免单次偶然。

```python run
import timeit

setup = "from math import sqrt"
stmt = "[sqrt(i) for i in range(100)]"
print(timeit.timeit(stmt, setup=setup, number=5000) < 2.0)
```


### 课堂延展：timeit 与 cProfile

本段补充对应 `docs/课程/20-性能/01-timeit与cProfile.md`，帮助把课文与阶段 20 项目里的真实文件对齐；建议边读边在仓库里搜索 `01-timeit与cProfile` 相关符号，而不是只扫一眼示例输出。

- 复盘目标 1：用 `timeit` 对小段代码做 **重复计时**，理解 `number` 与噪声。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 2：用 `cProfile` 找到 **热点函数** 与调用次数，而不是凭直觉猜瓶颈。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 3：建立「先 profile 再优化」的习惯，并知道微基准的局限。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 4：能把阶段 20 项目 `slow_math.py` 的两种实现放进对比实验。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 阶段 20 的相邻课程会反复出现同一术语；遇到陌生缩写时回到本课「对照」表，用 JS/Java 栏提醒自己 Python 的惯用写法。（01-timeit与cProfile·1）
- 读仓库代码时优先打开 `examples/项目/` 下与本课编号接近的目录，观察模块边界与 `if __name__ == '__main__'` 入口是否分离。（01-timeit与cProfile·2）
- 若 Pyodide 与本地输出存在细小差异，以 `uv run python tests/check_course.py -k 20-性能` 为准；浏览器端主要用于交互体验。（01-timeit与cProfile·3）
- 把本课一个 `python run` 块复制到临时文件单跑，改坏一处再修回来，比通读全文更能发现隐含的 API 约束。（01-timeit与cProfile·4）
- 写练习前先让 starter 故意失败一次，确认 check 段真的会捕获错误；这与阶段 15 的测试思维一致。（01-timeit与cProfile·5）
- 小结里的链接尽量点开一次：官方文档的「另见」小节常包含本课未展开但项目会遇到的边角行为。（01-timeit与cProfile·6）
- 团队评审时可用本课「易错点」当检查清单，对 PR 逐条问「有没有踩到这一条」。（01-timeit与cProfile·7）
- 若你维护 fork 课程站，请保持 frontmatter `title` 与 H1 一致，避免站内搜索出现双标题。（01-timeit与cProfile·8）

下面再跑一个与《01-timeit与cProfile》主题相关的小例子，巩固「能执行、能改、能解释输出」：

```python run
data = list(range(100))
print(len([x for x in data if x % 2 == 0]) == 50)
```

自测题（docs/课程/20-性能/01-timeit与cProfile.md·0）：若让你向同事用三分钟讲清「20.1 timeit 与 cProfile」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/20-性能/01-timeit与cProfile.md·1）：若让你向同事用三分钟讲清「20.1 timeit 与 cProfile」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/20-性能/01-timeit与cProfile.md·2）：若让你向同事用三分钟讲清「20.1 timeit 与 cProfile」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/20-性能/01-timeit与cProfile.md·3）：若让你向同事用三分钟讲清「20.1 timeit 与 cProfile」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/20-性能/01-timeit与cProfile.md·4）：若让你向同事用三分钟讲清「20.1 timeit 与 cProfile」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/20-性能/01-timeit与cProfile.md·5）：若让你向同事用三分钟讲清「20.1 timeit 与 cProfile」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/20-性能/01-timeit与cProfile.md·6）：若让你向同事用三分钟讲清「20.1 timeit 与 cProfile」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/20-性能/01-timeit与cProfile.md·7）：若让你向同事用三分钟讲清「20.1 timeit 与 cProfile」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/20-性能/01-timeit与cProfile.md·8）：若让你向同事用三分钟讲清「20.1 timeit 与 cProfile」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/20-性能/01-timeit与cProfile.md·9）：若让你向同事用三分钟讲清「20.1 timeit 与 cProfile」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/20-性能/01-timeit与cProfile.md·10）：若让你向同事用三分钟讲清「20.1 timeit 与 cProfile」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/20-性能/01-timeit与cProfile.md·11）：若让你向同事用三分钟讲清「20.1 timeit 与 cProfile」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/20-性能/01-timeit与cProfile.md·12）：若让你向同事用三分钟讲清「20.1 timeit 与 cProfile」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/20-性能/01-timeit与cProfile.md·13）：若让你向同事用三分钟讲清「20.1 timeit 与 cProfile」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/20-性能/01-timeit与cProfile.md·14）：若让你向同事用三分钟讲清「20.1 timeit 与 cProfile」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/20-性能/01-timeit与cProfile.md·15）：若让你向同事用三分钟讲清「20.1 timeit 与 cProfile」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/20-性能/01-timeit与cProfile.md·16）：若让你向同事用三分钟讲清「20.1 timeit 与 cProfile」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/20-性能/01-timeit与cProfile.md·17）：若让你向同事用三分钟讲清「20.1 timeit 与 cProfile」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/20-性能/01-timeit与cProfile.md·18）：若让你向同事用三分钟讲清「20.1 timeit 与 cProfile」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/20-性能/01-timeit与cProfile.md·19）：若让你向同事用三分钟讲清「20.1 timeit 与 cProfile」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/20-性能/01-timeit与cProfile.md·20）：若让你向同事用三分钟讲清「20.1 timeit 与 cProfile」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/20-性能/01-timeit与cProfile.md·21）：若让你向同事用三分钟讲清「20.1 timeit 与 cProfile」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/20-性能/01-timeit与cProfile.md·22）：若让你向同事用三分钟讲清「20.1 timeit 与 cProfile」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/20-性能/01-timeit与cProfile.md·23）：若让你向同事用三分钟讲清「20.1 timeit 与 cProfile」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/20-性能/01-timeit与cProfile.md·24）：若让你向同事用三分钟讲清「20.1 timeit 与 cProfile」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/20-性能/01-timeit与cProfile.md·25）：若让你向同事用三分钟讲清「20.1 timeit 与 cProfile」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/20-性能/01-timeit与cProfile.md·26）：若让你向同事用三分钟讲清「20.1 timeit 与 cProfile」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/20-性能/01-timeit与cProfile.md·27）：若让你向同事用三分钟讲清「20.1 timeit 与 cProfile」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/20-性能/01-timeit与cProfile.md·28）：若让你向同事用三分钟讲清「20.1 timeit 与 cProfile」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/20-性能/01-timeit与cProfile.md·29）：若让你向同事用三分钟讲清「20.1 timeit 与 cProfile」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。

## 易错点

- **只运行一次 `time.time()` 差值**：冷启动、GC、其他进程噪声会误导。
- **在调试模式或带 logging 的路径上微基准**：与生产路径不一致。
- **优化未热点的函数**：cProfile 已显示时间花在 `json.loads`，却去改变量名。
- **在 Pyodide/浏览器与服务器环境对比绝对时间**：只比同环境内的相对关系。

错误地把 timeit 返回值当「单次耗时」：

```python run raises=AssertionError
import timeit

total = timeit.timeit("1+1", number=1_000_000)
assert total < 0.000001, "这是百万次总时间，不是一次"
```

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 微基准 | `timeit` | `console.time` / benchmark.js | JMH |
| 调用统计 | `cProfile` / `profile` | Chrome Performance | VisualVM / async-profiler |
| 行级分析 | `line_profiler`（第三方） | 浏览器 DevTools | JProfiler |
| 原则 | 先测量 | 先测量 | 先测量 |
| 生产监控 | `logging` + APM | OpenTelemetry | Micrometer |

## 读代码

`examples/项目/20-优化慢函数/slow_math.py` 提供同一数学结果的两种实现：

```python source=examples/项目/20-优化慢函数/slow_math.py
"""可优化与不可优化对比（阶段 20）。"""
from __future__ import annotations

import cProfile
import io
import pstats
import timeit
from collections.abc import Callable


def _validate_n(n: int) -> None:
    if n < 0:
        raise ValueError("n 不能为负数")


def sum_squares_slow(n: int) -> int:
    _validate_n(n)
    total = 0
    for i in range(n):
        total += i * i
    return total


def sum_squares_fast(n: int) -> int:
    _validate_n(n)
    # n*(n-1)*(2n-1)//6
    return n * (n - 1) * (2 * n - 1) // 6


def benchmark_pair(
    n: int,
    *,
    number: int = 100,
    repeat: int = 3,
) -> dict[str, float]:
    _validate_n(n)
    if number < 1 or repeat < 1:
        raise ValueError("number 与 repeat 至少为 1")
    slow = min(timeit.repeat(lambda: sum_squares_slow(n), number=number, repeat=repeat))
    fast = min(timeit.repeat(lambda: sum_squares_fast(n), number=number, repeat=repeat))
    return {"slow_sec": slow, "fast_sec": fast, "speedup": slow / fast if fast else float("inf")}


def profile_function(func: Callable[[int], int], n: int, *, top_n: int = 5) -> str:
    _validate_n(n)
    profiler = cProfile.Profile()
    profiler.enable()
    func(n)
    profiler.disable()
    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.strip_dirs().sort_stats("cumulative").print_stats(top_n)
    return stream.getvalue()
```

- `sum_squares_slow`：O(n) 循环，适合作为 cProfile 里的「大山」。
- `sum_squares_fast`：O(1) 闭式公式，展示 **算法级** 优化幅度。
- `benchmark_pair`：用 `timeit.repeat` 返回 `slow_sec` / `fast_sec` / `speedup`，与课文计时实验一致。
- `profile_function`：封装 `cProfile` + `pstats`，测试断言输出含 `function calls`。
- `test_slow_math.py` 对多个 `n` 断言两者相等，并覆盖负 `n` 的 `ValueError`。

本地对比计时：

```bash
cd examples/项目/20-优化慢函数 && uv run python -c "import timeit; from slow_math import sum_squares_slow, sum_squares_fast; n=8000; print('slow', timeit.timeit(lambda: sum_squares_slow(n), number=50)); print('fast', timeit.timeit(lambda: sum_squares_fast(n), number=50))"
```

记录结果时写上 `n`、`number`、机器型号与 Python 版本（本仓库 3.12），否则三个月后无法判断某次「快 10 倍」是否仍可复现。阶段 18 的线程实验也应遵守同一记录规范。

`cProfile` 输出默认按 `cumulative` 排序时，内置 C 函数可能占比很高但无法优化；应展开到 **你自己项目的 .py 文件** 行号，再决定改哪一段循环。

**测量反模式（避免）**：

- 在 `-O` 优化或不同 `PYTHONHASHSEED` 下对比旧数据。
- 只测冷启动第一次请求，未计入连接池预热。
- 把 `print` 留在热点循环里却声称优化了算法。
- 用调试器单步执行代替批量 `timeit`。

若 `timeit` 显示快版本更慢，先检查是否测错了函数、是否在冷缓存上比较，而不是立刻否定算法推导。

`cProfile` 会显著放慢程序；不要在生产环境长期开启，仅用于诊断会话。

比较两次 `timeit` 结果时，使用比值（slow/fast）比绝对秒数更易在不同机器间交流结论。

profile 结果里的 `percall` 列在调用次数极大时接近 0 仍可能有累计意义，应结合 `ncalls` 阅读。

下一课 20.2 从复杂度角度解释为何 `sum_squares_fast` 值得替换慢循环。

把测量输出粘贴到 PR 描述里，是性能相关改动最受信赖的说明方式之一。

没有数字的性能 PR 应被要求补充基准或说明为何无法测量。

## 练习

### 练习 1：求 0..n-1 之和

实现 `sum_upto(n: int) -> int`：返回 `0 + 1 + ... + (n-1)`；`n<=0` 时返回 0。

```python exercise id=s20-l01-time
# --- starter ---
def sum_upto(n: int) -> int:
    return -1
# --- solution ---
def sum_upto(n: int) -> int:
    if n <= 0:
        return 0
    return n * (n - 1) // 2
# --- check ---
assert sum_upto(10) == 45
assert sum_upto(0) == 0
assert sum_upto(1) == 0
```

### 练习 2：选择更快的求和实现

实现 `pick_fast_sum()`：返回内置 `sum` 可调用对象（用于与手写循环对比的课内实验）。

```python exercise id=s20-l01-sum
# --- starter ---
def pick_fast_sum():
    return None
# --- solution ---
def pick_fast_sum():
    return sum
# --- check ---
assert pick_fast_sum()(range(5)) == 10
```

## 小结

- `timeit` 要配合合适的 `number`；比较相对速度，别迷信单次。
- `cProfile.Profile().runcall` 适合定位热点；先 profile 再改代码。
- `slow_math.py` 是「同结果、不同复杂度」的标准教具。
- 阶段 18 并发选型也应以测量为依据，而非默认多线程。
- `Profile.runcall` 在课内与 Pyodide 中比 `cProfile.run('fn()')` 更可靠。
- 记录基准时请写下 `n` 与 `number` 参数。
- 对比 `slow_math` 两实现是阶段 20 的固定实验作业。

## 延伸阅读

- [timeit — 测量小代码片段执行时间](https://docs.python.org/zh-cn/3/library/timeit.html)
- [Python Profilers](https://docs.python.org/zh-cn/3/library/profile.html)
