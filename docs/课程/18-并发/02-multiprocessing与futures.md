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

def describe(fut: Future[int], label: str) -> None:
    print(label, "done=", fut.done(), "cancelled=", fut.cancelled())

fut: Future[int] = Future()
describe(fut, "新建")
fut.set_result(100)
describe(fut, "set_result 后")
value = fut.result()
print("result()=", value, "type=", type(value).__name__)
```

`describe` 在设置结果前后各打印一次状态：未完成时 `done` 为假，调用 `set_result` 后变为真且 `result()` 立刻返回 100。这对应线程池 worker 在任务结束时替你把 Future 标记完成；课内用手动 `set_result` 理解 API，而不启动真实池子。

### Executor 接口：submit 与 map

- `submit(fn, *args)` → 单个 `Future`，灵活但结果顺序要自己做。
- `executor.map(fn, iterable)` → **按输入顺序** 迭代结果，适合同构批量任务。

用列表推导模拟 `map` 的「保序」语义（与线程无关，便于课内运行）：

```python run
def fetch_label(url: str) -> str:
    return f"body:{url}"

def map_in_order(fn, items: list[str]) -> list[str]:
    return [fn(x) for x in items]

def completion_order(finish_ms: list[int]) -> list[int]:
    return [i for i, _ in sorted(enumerate(finish_ms), key=lambda p: p[1])]

urls = ["c", "a", "b"]
mapped = map_in_order(fetch_label, urls)
finished_first = completion_order([30, 5, 12])
print("map 保序", mapped)
print("完成先后索引", finished_first)
print("同批 URL 数", len(urls), len(mapped))
```

`map_in_order` 模拟 `executor.map`：输出顺序始终与 `urls` 一致。`completion_order` 用假定的完成毫秒说明 `as_completed` 按完成先后迭代，索引 `[1,2,0]` 与 map 的 `['c','a','b']` 不同——读下载器代码时要分清「保序 map」与「谁先完成谁先取」。

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
def default_thread_workers(logical_cpus: int) -> int:
    return min(32, logical_cpus + 4)

def suggest_pool(workload: str, cpus: int) -> str:
    if workload == "io":
        return f"thread≈{default_thread_workers(cpus)}"
    return f"process≈{cpus}"

cpus = 4
io_workers = default_thread_workers(cpus)
cpu_workers = cpus
print("logical_cpus", cpus)
print("默认线程池上限", io_workers)
print("I/O 建议", suggest_pool("io", cpus))
print("CPU 建议", suggest_pool("cpu", cpus))
```

标准库线程池默认 `min(32, cpu_count+4)`，课内用 4 核得到 8。I/O 密集可接近该上限重叠等待；CPU 密集进程池通常不超过核数，否则切换开销会吞掉收益。在长时间服务里，更常见的是在 `with` 块退出时自动 `shutdown`，或显式 `executor.shutdown(cancel_futures=True)` 放弃未开始的任务（3.9+ `cancel_futures` 参数）。读服务端代码时看到 `wait=False` 要警惕：主线程可能先退出而任务仍在跑。

课内用已完成的 `Future` 模拟 `as_completed` 的「先完成先取结果」语义（不启动线程）：

```python run
from concurrent.futures import Future

def drain_done(futs: list[Future[int]]) -> list[int]:
    pending = list(futs)
    out: list[int] = []
    while pending:
        for f in list(pending):
            if f.done():
                out.append(f.result())
                pending.remove(f)
    return out

slow, fast = Future(), Future()
fast.set_result(2)
slow.set_result(1)
print(drain_done([slow, fast]))
```

本地进程池（CPU 密集、可 pickle 的顶层函数）：

```python local
import os
from concurrent.futures import ProcessPoolExecutor

cpus = os.cpu_count() or 1
# 在独立 .py 模块里定义顶层 def 任务函数，再在本机运行进程池（校验器子进程内无法 pickle 临时脚本里的函数）
print(cpus, ProcessPoolExecutor is not None)
```

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
