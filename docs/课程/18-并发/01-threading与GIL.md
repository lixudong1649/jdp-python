---
title: 18.1 threading 与 GIL
---

# 18.1 threading 与 GIL

> 前置：3. 控制流、16.x 工具链 · 约 35 分钟 · 官方对应：[threading](https://docs.python.org/zh-cn/3/library/threading.html)、[GIL FAQ](https://docs.python.org/zh-cn/3/faq/library.html#what-kinds-of-global-value-mutation-are-thread-safe) · 核对日期 2026-10-18（课程环境 Python 3.12；稳定版 3.15；free-threaded 自 3.14 起可选，见 18.3）

## 目标

- 说清楚 **GIL（全局解释器锁）** 为何让多线程难以并行执行 CPU 密集字节码。
- 区分 **CPU 密集** 与 **I/O 等待**：后者仍可用线程或异步重叠等待时间。
- 会用 `threading.Lock` 保护共享可变状态，并知道 `int += 1` 不是原子操作。
- 能在本仓库阶段项目里指出「模拟下载」为何选线程池。

## 核心概念

### GIL 与「并行」的直觉

CPython 解释器在同一时刻通常只让一个线程执行 Python 字节码（GIL）。因此四个线程各做大量纯 Python 循环，**总耗时往往接近单线程四倍**，而不是四分之一。

下面用**单线程**重复四次相同工作量，作为「无并行收益」的基线（浏览器课内无法启动真实 OS 线程，完整多线程对比请在本地跑阶段项目）：

```python run
def cpu_chunk(n: int) -> int:
    total = 0
    for i in range(n):
        total += i % 7
    return total

N = 8_000
once = cpu_chunk(N)
serial = sum(cpu_chunk(N) for _ in range(4))
print(once > 0, serial == once * 4)
```

真实线程在本地可重叠 **I/O**（磁盘、网络、`time.sleep`），那才是阶段 18 线程池的主战场。

若你已在 macOS/Linux 安装 CPython，可用下面一行感受多线程调度（**不要**放进课程 `python run` 块，以免 Pyodide 报错）：

```python
import threading, time

def worker(tag: str) -> None:
    time.sleep(0.05)
    print(tag)

for name in ("A", "B"):
    threading.Thread(target=worker, args=(name,)).start()
```

输出顺序不固定，但总耗时明显短于两次顺序 `sleep(0.05)`。

### 共享状态：为何需要锁

多个线程同时执行 `counter += 1` 时，读—改—写可能被交错，最终计数小于预期。锁保证「临界区」内只有一个线程在执行。

课内演示锁的 **API**（同一线程 acquire/release；浏览器环境不启动子线程）：

```python local
import threading

counter = {"n": 0}
lock = threading.Lock()

def safe_add(times: int) -> None:
    with lock:
        for _ in range(times):
            counter["n"] += 1

safe_add(1_000)
print(counter["n"], lock.locked() is False)
```

浏览器里用「单线程 + 上下文管理器」理解锁的临界区语义（与 `threading.Lock` 的 `with` 形状相同）：

```python run
class CriticalSection:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False

counter = {"n": 0}
with CriticalSection():
    for _ in range(1_000):
        counter["n"] += 1
print(counter["n"] == 1_000)
```

`with lock:` 等价于 `acquire` 成功后在 `finally` 里 `release`，避免忘记释放。

### 何时考虑线程

| 场景 | 更常见选择 | 原因 |
|---|---|---|
| 大量 `requests` / 读文件等待 | `ThreadPoolExecutor` 或 asyncio | 线程阻塞在 I/O 时会释放 GIL |
| 纯 Python 数值循环 | `multiprocessing` / 重写算法 / 扩展模块 | GIL 限制 CPU 并行 |
| 少量后台任务 | `threading.Thread` | 注意共享状态与优雅退出 |

本地用线程池并发「下载」的完整代码见 `examples/项目/18-并发下载模拟/`（下文读代码）。

## 易错点

- **以为「开了 8 个线程就快 8 倍」**：CPU 密集纯 Python 往往几乎不变；要先 profile（阶段 20）再选模型。
- **`global` 变量 + 无锁自增**：丢更新；用 `Lock` 或 `queue.Queue` 传递结果。
- **在 import 阶段起线程**：模块副作用难测；优先显式 `main` 或池化入口。
- **把 `daemon=True` 当优雅退出**：守护线程会被硬切；需要 join 或事件通知。

未加锁的自增在逻辑上可能「看起来对」，但并发下不可靠；下面用**故意错误的顺序**模拟竞态（单线程无法复现丢更新，但展示非原子读改写）：

```python run raises=KeyError
state = {}
# 误以为可以靠「最后一次写入」代替锁
state["n"] = state.get("n", 0) + 1
del state["n"]
print(state["n"])
```

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 轻量并发单元 | `threading.Thread` | Web Worker（无共享堆） | `Thread` |
| 互斥 | `threading.Lock` / `RLock` | 无共享内存，靠消息 | `synchronized` / `ReentrantLock` |
| CPU 并行同一进程 | GIL 限制 CPython 字节码 | 单线程事件循环为主 | 真并行（受核心数限制） |
| 池化 API | `concurrent.futures` | 手动 Promise 池 | `ExecutorService` |
| 重叠 I/O | 线程或 asyncio | `async`/`await` | NIO / 虚拟线程（21+） |

## 读代码

阶段项目 `examples/项目/18-并发下载模拟/downloader.py` 用 **线程池 + `as_completed`** 模拟多个 URL 同时下载（`time.sleep` 代表网络等待）：

```python source=examples/项目/18-并发下载模拟/downloader.py
"""模拟并发下载（线程池，阶段 18）。"""
from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field


class DownloadError(Exception):
    """下载失败（模拟 HTTP 错误或超时）。"""

    def __init__(self, url: str, reason: str) -> None:
        self.url = url
        self.reason = reason
        super().__init__(f"{url}: {reason}")


@dataclass
class FetchOutcome:
    url: str
    body: str | None = None
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None


@dataclass
class BatchResult:
    bodies: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def fetch(url: str, delay: float = 0.01, *, fail_if: str | None = None) -> str:
    if not url.strip():
        raise ValueError("url 不能为空")
    time.sleep(delay)
    if fail_if and fail_if in url:
        raise DownloadError(url, "simulated failure")
    return f"body:{url}"


def _safe_fetch(url: str, delay: float, fail_if: str | None) -> FetchOutcome:
    try:
        return FetchOutcome(url=url, body=fetch(url, delay, fail_if=fail_if))
    except DownloadError as e:
        return FetchOutcome(url=url, error=str(e))


def download_all(
    urls: list[str],
    *,
    workers: int = 4,
    delay: float = 0.01,
    fail_if: str | None = None,
    raise_on_error: bool = False,
) -> list[str]:
    if workers < 1:
        raise ValueError("workers 至少为 1")
    if not urls:
        return []
    result = BatchResult()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_safe_fetch, u, delay, fail_if): u for u in urls}
        for fut in as_completed(futures):
            outcome = fut.result()
            if outcome.ok and outcome.body is not None:
                result.bodies.append(outcome.body)
            elif outcome.error:
                result.errors.append(outcome.error)
    if raise_on_error and result.errors:
        raise DownloadError("batch", result.errors[0])
    return sorted(result.bodies)
```

- 第 9–15 行：`DownloadError` 表示单次下载失败；`FetchOutcome` / `BatchResult` 把成功体与错误信息分开收集。
- 第 35–41 行：`fetch` 是 **I/O 型**占位（`time.sleep`）；`fail_if` 用于测试里模拟坏 URL。
- 第 44–48 行：`_safe_fetch` 捕获 `DownloadError`，避免一个 future 的异常直接打断 `as_completed` 循环。
- 第 64–74 行：`ThreadPoolExecutor` + `as_completed` 按完成顺序汇总；`sorted` 让测试输出稳定；`raise_on_error` 覆盖严格失败路径。

本地验证：

```bash
cd examples/项目/18-并发下载模拟 && uv run pytest -q
```

## 练习

### 练习 1：非阻塞尝试加锁

实现 `try_increment(counter, lock)`：若 `lock.acquire(blocking=False)` 成功则 `counter["v"] += 1` 并释放锁，返回是否成功；否则返回 `False`。

```python local exercise id=s18-l01-thread
# --- starter ---
import threading

def try_increment(counter: dict, lock: threading.Lock) -> bool:
    return False
# --- solution ---
import threading

def try_increment(counter: dict, lock: threading.Lock) -> bool:
    if not lock.acquire(blocking=False):
        return False
    try:
        counter["v"] = counter.get("v", 0) + 1
        return True
    finally:
        lock.release()
# --- check ---
c: dict = {}
lk = threading.Lock()
assert try_increment(c, lk) is True
assert c["v"] == 1
lk.acquire()
assert try_increment(c, lk) is False
lk.release()
```

### 练习 2：带锁的批量自增

实现 `bump_many(counter, lock, times)`：在持锁期间循环 `times` 次，每次 `counter["total"] += 1`；返回最终 `total`。

```python local exercise id=s18-l01-bump
# --- starter ---
import threading

def bump_many(counter: dict, lock: threading.Lock, times: int) -> int:
    return 0
# --- solution ---
import threading

def bump_many(counter: dict, lock: threading.Lock, times: int) -> int:
    with lock:
        counter.setdefault("total", 0)
        for _ in range(times):
            counter["total"] += 1
        return counter["total"]
# --- check ---
c: dict = {}
lk = threading.Lock()
assert bump_many(c, lk, 5) == 5
assert bump_many(c, lk, 3) == 8
```

## 小结

- CPython 的 GIL 让多线程不适合「纯 Python CPU 并行」，但适合重叠 I/O 等待。
- 共享可变状态要用锁或消息传递；`+=` 不是原子操作。
- 读 `downloader.py`：线程池 + `as_completed` + 最后排序，是常见的批量 I/O 模板。
- 浏览器课内不跑真实线程；本地用阶段项目与 pytest 验证并发行为。

## 延伸阅读

- [threading — 基于线程的并行](https://docs.python.org/zh-cn/3/library/threading.html)
- [FAQ：哪些全局修改是线程安全的？](https://docs.python.org/zh-cn/3/faq/library.html#what-kinds-of-global-value-mutation-are-thread-safe)
