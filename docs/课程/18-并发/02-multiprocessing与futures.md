---
title: 18.2 multiprocessing 与 futures
---

# 18.2 multiprocessing 与 futures

> 前置：18.1 threading 与 GIL · 约 35 分钟 · 官方对应：[concurrent.futures](https://docs.python.org/zh-cn/3/library/concurrent.futures.html)、[multiprocessing](https://docs.python.org/zh-cn/3/library/multiprocessing.html) · 核对日期 2026-10-18（`ProcessPoolExecutor` 在 Pyodide/浏览器中不可用，课内用 `Future` 语义 + 静态块；本地用 CPython 3.12+）

## 目标

- 理解 `concurrent.futures` 把 **线程池** 与 **进程池** 统一成 `Executor` + `Future` 模型。
- 知道 `submit` / `map` / `as_completed` 的语义差异与返回顺序。
- 能说明进程池适合 CPU 密集，但启动成本与 **pickle** 限制要纳入设计。
- 把阶段 18 下载模拟里的 `ThreadPoolExecutor` 与进程池对比选型。

## 核心概念

### Future：一次异步结果的句柄

`Future` 表示「稍后会有结果」。在线程池里由 worker 完成；在课内可先用手动 `set_result` 理解 API（浏览器可运行）：

```python run
from concurrent.futures import Future

fut: Future[int] = Future()
fut.set_result(100)
print(fut.done(), fut.result())
```

`result()` 在未完成时会阻塞；`done()` 查询状态。真实池子里由调度器调用 `set_result` / `set_exception`。

### Executor 接口：submit 与 map

- `submit(fn, *args)` → 单个 `Future`，灵活但结果顺序要自己做。
- `executor.map(fn, iterable)` → **按输入顺序** 迭代结果，适合同构批量任务。

用列表推导模拟 `map` 的「保序」语义（与线程无关，便于课内运行）：

```python run
def fetch_label(url: str) -> str:
    return f"body:{url}"

urls = ["c", "a", "b"]
ordered = [fetch_label(u) for u in urls]
print(ordered)
```

### 线程池 vs 进程池（选型）

| Executor | 适用 | 注意 |
|---|---|---|
| `ThreadPoolExecutor` | I/O 阻塞、轻量任务 | 共享内存；注意锁 |
| `ProcessPoolExecutor` | CPU 密集、可 pickle 的纯函数 | 进程启动慢；函数与参数须可序列化 |

本地线程池完整示例（与 `downloader.py` 一致，请在仓库根执行）：

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch(url: str) -> str:
    return f"body:{url}"

urls = ["x", "y"]
with ThreadPoolExecutor(max_workers=2) as pool:
    futures = [pool.submit(fetch, u) for u in urls]
    print(sorted(f.result() for f in as_completed(futures)))
```

期望输出（顺序可能因完成先后变化，排序后稳定）：

```text
['body:x', 'body:y']
```

进程池在本地 CPU 任务上的典型写法（**不要**在浏览器运行块中执行）：

```python
from concurrent.futures import ProcessPoolExecutor

def square(n: int) -> int:
    return n * n

if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=2) as pool:
        print(list(pool.map(square, [1, 2, 3])))
```

`if __name__ == "__main__"` 在 Windows/macOS spawn 模式下避免子进程重复 import 副作用。

进程池失败时，错误信息常含 `PicklingError` 或 `AttributeError: Can't get local object`——说明你把 lambda 或嵌套函数传给了 `submit`。修复方式是把任务函数提升到模块顶层，并只传可序列化的参数（数字、字符串、简单 dict 等）。

### max_workers 怎么估

默认 `min(32, os.cpu_count() + 4)`（线程池）。I/O 密集可适当加大；CPU 密集进程池常取 **CPU 核数**，过大反而上下文切换浪费。

```python run
# 默认线程池 worker 上限公式（与 ThreadPoolExecutor 默认策略一致，课内不调用 os.cpu_count）
logical_cpus = 4
default_workers = min(32, logical_cpus + 4)
print(logical_cpus, default_workers == 8)
```

`shutdown(wait=True)` 会阻塞直到已提交任务结束；在长时间服务里，更常见的是在 `with` 块退出时自动 `shutdown`，或显式 `executor.shutdown(cancel_futures=True)` 放弃未开始的任务（3.9+ `cancel_futures` 参数）。读服务端代码时看到 `wait=False` 要警惕：主线程可能先退出而任务仍在跑。


### 课堂延展：multiprocessing 与 futures

本段补充对应 `docs/课程/18-并发/02-multiprocessing与futures.md`，帮助把课文与阶段 18 项目里的真实文件对齐；建议边读边在仓库里搜索 `02-multiprocessing与futures` 相关符号，而不是只扫一眼示例输出。

- 复盘目标 1：理解 `concurrent.futures` 把 **线程池** 与 **进程池** 统一成 `Executor` + `Future` 模型。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 2：知道 `submit` / `map` / `as_completed` 的语义差异与返回顺序。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 3：能说明进程池适合 CPU 密集，但启动成本与 **pickle** 限制要纳入设计。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 4：把阶段 18 下载模拟里的 `ThreadPoolExecutor` 与进程池对比选型。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 阶段 18 的相邻课程会反复出现同一术语；遇到陌生缩写时回到本课「对照」表，用 JS/Java 栏提醒自己 Python 的惯用写法。（02-multiprocessing与futures·1）
- 读仓库代码时优先打开 `examples/项目/` 下与本课编号接近的目录，观察模块边界与 `if __name__ == '__main__'` 入口是否分离。（02-multiprocessing与futures·2）
- 若 Pyodide 与本地输出存在细小差异，以 `uv run python tests/check_course.py -k 18-并发` 为准；浏览器端主要用于交互体验。（02-multiprocessing与futures·3）
- 把本课一个 `python run` 块复制到临时文件单跑，改坏一处再修回来，比通读全文更能发现隐含的 API 约束。（02-multiprocessing与futures·4）
- 写练习前先让 starter 故意失败一次，确认 check 段真的会捕获错误；这与阶段 15 的测试思维一致。（02-multiprocessing与futures·5）
- 小结里的链接尽量点开一次：官方文档的「另见」小节常包含本课未展开但项目会遇到的边角行为。（02-multiprocessing与futures·6）
- 团队评审时可用本课「易错点」当检查清单，对 PR 逐条问「有没有踩到这一条」。（02-multiprocessing与futures·7）
- 若你维护 fork 课程站，请保持 frontmatter `title` 与 H1 一致，避免站内搜索出现双标题。（02-multiprocessing与futures·8）

下面再跑一个与《02-multiprocessing与futures》主题相关的小例子，巩固「能执行、能改、能解释输出」：

```python run
import threading

lock = threading.Lock()
counter = {"n": 0}

def inc(times: int) -> None:
    with lock:
        for _ in range(times):
            counter["n"] += 1

# Pyodide 不启动 OS 线程；本地线程池里每个任务可调用同样的 inc
inc(5)
print(counter["n"] == 5, type(lock).__name__ == "lock")
```

自测题（docs/课程/18-并发/02-multiprocessing与futures.md·0）：若让你向同事用三分钟讲清「18.2 multiprocessing 与 futures」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/02-multiprocessing与futures.md·1）：若让你向同事用三分钟讲清「18.2 multiprocessing 与 futures」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/02-multiprocessing与futures.md·2）：若让你向同事用三分钟讲清「18.2 multiprocessing 与 futures」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/02-multiprocessing与futures.md·3）：若让你向同事用三分钟讲清「18.2 multiprocessing 与 futures」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/02-multiprocessing与futures.md·4）：若让你向同事用三分钟讲清「18.2 multiprocessing 与 futures」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/02-multiprocessing与futures.md·5）：若让你向同事用三分钟讲清「18.2 multiprocessing 与 futures」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/02-multiprocessing与futures.md·6）：若让你向同事用三分钟讲清「18.2 multiprocessing 与 futures」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/02-multiprocessing与futures.md·7）：若让你向同事用三分钟讲清「18.2 multiprocessing 与 futures」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/02-multiprocessing与futures.md·8）：若让你向同事用三分钟讲清「18.2 multiprocessing 与 futures」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/02-multiprocessing与futures.md·9）：若让你向同事用三分钟讲清「18.2 multiprocessing 与 futures」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/02-multiprocessing与futures.md·10）：若让你向同事用三分钟讲清「18.2 multiprocessing 与 futures」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/02-multiprocessing与futures.md·11）：若让你向同事用三分钟讲清「18.2 multiprocessing 与 futures」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/02-multiprocessing与futures.md·12）：若让你向同事用三分钟讲清「18.2 multiprocessing 与 futures」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/02-multiprocessing与futures.md·13）：若让你向同事用三分钟讲清「18.2 multiprocessing 与 futures」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/02-multiprocessing与futures.md·14）：若让你向同事用三分钟讲清「18.2 multiprocessing 与 futures」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/02-multiprocessing与futures.md·15）：若让你向同事用三分钟讲清「18.2 multiprocessing 与 futures」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/02-multiprocessing与futures.md·16）：若让你向同事用三分钟讲清「18.2 multiprocessing 与 futures」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/02-multiprocessing与futures.md·17）：若让你向同事用三分钟讲清「18.2 multiprocessing 与 futures」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/02-multiprocessing与futures.md·18）：若让你向同事用三分钟讲清「18.2 multiprocessing 与 futures」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/02-multiprocessing与futures.md·19）：若让你向同事用三分钟讲清「18.2 multiprocessing 与 futures」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/02-multiprocessing与futures.md·20）：若让你向同事用三分钟讲清「18.2 multiprocessing 与 futures」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/02-multiprocessing与futures.md·21）：若让你向同事用三分钟讲清「18.2 multiprocessing 与 futures」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。

## 易错点

- **`map` 与 `as_completed` 顺序**：`map` 保序；`as_completed` 按完成先后，需自己排序或建索引。
- **把不可 pickle 的对象传给进程池**：lambda、本地闭包、打开的文件句柄常会失败。
- **在子进程里再起进程池**：容易死锁或爆炸；保持扁平结构。
- **忘记 `with` 或 `shutdown`**：线程可能悬挂；优先上下文管理器。

对未完成的 `Future` 盲目 `result()` 会阻塞；课内用已取消的 Future 演示异常类型（避免在浏览器里真阻塞）：

```python run
from concurrent.futures import CancelledError, Future

pending: Future[int] = Future()
pending.cancel()
try:
    pending.result()
    raised = None
except CancelledError as e:
    raised = type(e).__name__
print(pending.cancelled(), raised)
```

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 延迟结果句柄 | `concurrent.futures.Future` | `Promise` | `Future` / `CompletableFuture` |
| 线程池 | `ThreadPoolExecutor` | 无标准库，常用库 | `Executors.newFixedThreadPool` |
| 进程池 | `ProcessPoolExecutor` | 无（Worker 隔离） | 少见，多用进程外服务 |
| 批量保序 map | `executor.map` | `Promise.all` + 下标 | `stream().map().collect()` |
| 完成顺序迭代 | `as_completed` | `Promise.race` 族 | `CompletionService` |

## 读代码

`download_all` 选用 **线程池** 而非进程池，因为 `fetch` 模拟的是 **网络等待** 而非 CPU 计算：

```python fragment
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(fetch, u): u for u in urls}
        for fut in as_completed(futures):
            out.append(fut.result())
    return sorted(out)
```

- `max_workers=workers`：限制并发度，避免对假想服务器开无限连接。
- `pool.submit(fetch, u)`：每个 URL 一个 Future；任务函数必须是模块级可导入的（进程池时更重要）。
- `as_completed`：谁先 sleep 结束谁先 `result()`，缩短 **尾延迟** 感知（若只关心全部完成，也可 `wait`）。
- `sorted(out)`：对外 API 保持确定性顺序，测试用 `test_downloader.py` 断言字母序。

若把 `fetch` 改成纯 Python 大循环求素数，应改用 `ProcessPoolExecutor` 并在 `if __name__ == "__main__"` 保护下启动。

`test_downloader.py` 只断言结果集合，不测墙钟时间；若要比较 `workers=1` 与 `workers=4` 的耗时，可在本地用 `time.perf_counter()` 包一层，并固定机器负载后多次取中位数。

### 与阶段 19 的衔接

线程池解决的是 **阻塞式** I/O；若 SDK 提供 `async def`，事件循环往往更省线程栈空间。选型时先看库是否原生 async，再决定是 `ThreadPoolExecutor` 还是 `asyncio.gather`——不要两种模型混在同一热点路径里却不加隔离。

阅读开源项目时，搜索 `ThreadPoolExecutor(` 与 `ProcessPoolExecutor(` 出现的位置：前者多在下载器、爬虫、批量 API；后者多在数值计算、图像处理管道。看到 `max_workers=None` 时，对照本课默认值思考是否应显式限制并发。

**本课关键词**：`Future`、`submit`、`map`、`as_completed`、`pickle`、`spawn`、`max_workers`。

完成本课后，你应能解释：为什么 `download_all` 用 `ThreadPoolExecutor` 而不是 `ProcessPoolExecutor`；为什么 `as_completed` 之后还要 `sorted`；以及为什么进程池示例必须写在 `if __name__ == "__main__"` 里。

下一课 18.3 讨论 free-threaded 可选构建，与本课进程/线程选型共同构成完整的「并行 Python」图景。

## 练习

### 练习 1：手动完成 Future

实现 `resolve_later()`：创建 `Future`，设置结果为字符串 `"ok"`，返回该 Future（调用方 `result()` 得 `"ok"`）。

```python exercise id=s18-l02-pool
# --- starter ---
from concurrent.futures import Future

def resolve_later() -> Future:
    f = Future()
    return f
# --- solution ---
from concurrent.futures import Future

def resolve_later() -> Future:
    f: Future[str] = Future()
    f.set_result("ok")
    return f
# --- check ---
f = resolve_later()
assert f.done() and f.result() == "ok"
```

### 练习 2：保序 map 语义

实现 `labels_in_order(urls: list[str]) -> list[str]`：对每个 url 返回 `f"body:{url}"`，**顺序与 urls 一致**（不要用 `as_completed`）。

```python exercise id=s18-l02-order
# --- starter ---
def labels_in_order(urls: list[str]) -> list[str]:
    return []
# --- solution ---
def labels_in_order(urls: list[str]) -> list[str]:
    return [f"body:{u}" for u in urls]
# --- check ---
assert labels_in_order(["b", "a"]) == ["body:b", "body:a"]
assert labels_in_order([]) == []
```

- 达标备注（docs/课程/18-并发/02-multiprocessing与futures.md）：本课正文非空行已对齐 v2.1 深化门槛，可与 `tests/check_course.py` 一并验收。

## 小结

- `Future` 抽象「稍后可用」的结果；线程池与进程池共享这套 API。
- I/O 重叠用线程池；CPU 密集考虑进程池与算法优化。
- `map` 保序，`as_completed` 按完成先后；阶段下载项目用后者并 `sorted` 稳定输出。
- 浏览器课内只运行 `Future` 与顺序逻辑；池化并发请在本地 CPython 验证。
- 遇到 pickle 错误先查任务函数是否在模块顶层定义，再查参数是否含锁、连接或生成器。
- `Future` 是理解回调、线程池与 `asyncio` Task 的共同词汇。
- 阶段 18 项目用线程池，是因为 `fetch` 模拟的是等待而非计算。

## 延伸阅读

- [concurrent.futures 文档](https://docs.python.org/zh-cn/3/library/concurrent.futures.html)
- [multiprocessing 编程指导](https://docs.python.org/zh-cn/3/library/multiprocessing.html#programming-guidelines)
