---
title: 19.2 gather 与 TaskGroup
---

# 19.2 gather 与 TaskGroup

> 前置：19.1 协程与事件循环 · 约 35 分钟 · 官方对应：[asyncio.gather](https://docs.python.org/zh-cn/3/library/asyncio-task.html#asyncio.gather)、[TaskGroup](https://docs.python.org/zh-cn/3/library/asyncio-task.html#task-groups)（TaskGroup 自 3.11 起） · 核对日期 2026-10-18（并发 await 示例在本地运行；课内检查 API 存在性）

## 目标

- 用 `asyncio.gather` 并发多个协程并收集结果顺序。
- 理解 `return_exceptions=True` 与默认「首异常即失败」的差异。
- 知道 `asyncio.TaskGroup` 提供 **结构化并发**：子任务失败会取消同组其余任务（3.11+）。
- 能把「并行多个 tool / 多个 HTTP」映射到 gather 或 TaskGroup 模式。

## 核心概念

### gather：并行等待多个 awaitable

`gather(*aws)` 把多个协程放进同一事件循环时间线；全部完成后返回 **元组**，顺序与传入参数一致（不是完成先后）。

本地可运行示例：

```python
import asyncio

async def tag(name: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return name

async def main() -> None:
    a, b = await asyncio.gather(tag("first", 0.01), tag("second", 0))
    print(a, b)

asyncio.run(main())
```

期望输出：`first second`（元组顺序与参数一致，尽管 `second` 可能先完成）。

### return_exceptions

默认任一子协程抛异常，`gather` 会把异常传给 await 方。若 `return_exceptions=True`，异常对象会作为对应位置的结果元素，其它任务仍运行完毕。

课内检查 `gather` 签名与模块归属（不启动循环）：

```python run
import asyncio
import inspect


def coro_work(name: str, ticks: int):
    for _ in range(ticks):
        yield
    return name


def mini_gather(*factories):
    gens = [(i, f()) for i, f in enumerate(factories)]
    results: list[str | None] = [None] * len(factories)
    finish_order: list[int] = []
    while gens:
        next_gens = []
        for i, g in gens:
            try:
                g.send(None)
                next_gens.append((i, g))
            except StopIteration as e:
                results[i] = e.value
                finish_order.append(i)
        gens = next_gens
    return tuple(results), finish_order


result_tuple, finished = mini_gather(
    lambda: coro_work("first", 2),
    lambda: coro_work("second", 1),
)
sig = inspect.signature(asyncio.gather)
print("gather 参数", list(sig.parameters)[:2])
print("结果元组顺序", result_tuple)
print("完成先后索引", finished)
print("元组顺序≠完成顺序", list(result_tuple) != [result_tuple[i] for i in finished])
```

课内无法 `asyncio.run`，用手写 `mini_gather` 驱动生成器协程：**返回元组仍按参数顺序**（`first` 在前），`finish_order` 记录谁先跑完（`second` 先结束）。读 `asyncio.gather` 签名时留意 `return_exceptions` 等参数，完整时序请在本地 `asyncio.run` 实验。

```python
async def main() -> None:
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(tag("a", 0))
        t2 = tg.create_task(tag("b", 0))
    print(t1.result(), t2.result())
```

任一 `create_task` 内未处理异常会导致 **整组取消**，适合「要么全成功要么全回滚」的语义。与 `gather` 相比，错误传播更严格。

课内确认当前解释器版本是否满足 TaskGroup（3.11+）：

```python run
def coro_step(name: str, steps: int, fail: bool = False):
    for i in range(steps):
        if fail and i == steps - 1:
            raise RuntimeError(f"{name} boom")
        yield
    return name


def drive_to_end(gen):
    try:
        while True:
            gen.send(None)
    except StopIteration as e:
        return "done", e.value
    except Exception as e:
        return "failed", type(e).__name__


def simulate_gather_fail_fast(factories):
    gens = [f() for f in factories]
    labels = ["slow_ok", "fast_fail"]
    states = {labels[i]: "pending" for i in range(len(gens))}
    results: dict[str, object] = {}
    gather_exc = None
    active = list(enumerate(gens))
    while active and gather_exc is None:
        nxt = []
        for i, g in active:
            try:
                g.send(None)
                nxt.append((i, g))
            except StopIteration as e:
                states[labels[i]] = "done"
                results[labels[i]] = e.value
            except Exception as e:
                states[labels[i]] = "failed"
                gather_exc = type(e).__name__
        active = nxt
    while active:
        nxt = []
        for i, g in active:
            try:
                g.send(None)
                nxt.append((i, g))
            except StopIteration as e:
                states[labels[i]] = "done"
                results[labels[i]] = e.value
        active = nxt
    return states, results, gather_exc


def simulate_task_group(factories):
    labels = ["peer_a", "peer_b"]
    gens = [f() for f in factories]
    states = {labels[i]: "pending" for i in range(len(gens))}
    group_error = None
    for i, g in enumerate(gens):
        if group_error:
            states[labels[i]] = "cancelled"
            continue
        status, detail = drive_to_end(g)
        states[labels[i]] = status
        if status == "failed":
            group_error = detail
            for j in range(i + 1, len(gens)):
                states[labels[j]] = "cancelled"
    return states, group_error


g_states, g_results, g_err = simulate_gather_fail_fast(
    [lambda: coro_step("slow_ok", 2), lambda: coro_step("fast_fail", 1, fail=True)]
)
tg_states, tg_err = simulate_task_group(
    [lambda: coro_step("peer_a", 2), lambda: coro_step("peer_b", 1, fail=True)]
)
print("gather states", g_states)
print("gather kept slow_ok result", g_results.get("slow_ok"))
print("gather propagated", g_err)
print("taskgroup states", tg_states)
print("taskgroup error", tg_err)
print("taskgroup cancelled count", sum(v == "cancelled" for v in tg_states.values()))
print("gather vs group", g_states["slow_ok"], tg_states["peer_a"])
```

`simulate_gather_fail_fast` 里 `fast_fail` 先抛错，但 `slow_ok` 仍有机会跑完并被记入 `results`；`simulate_task_group` 在 `peer_b` 失败后把尚未驱动的 `peer_a` 标成 `cancelled`。课内不用 `asyncio.run`，用手写 `send` 逐步驱动生成器协程，对照「异常向外传播时兄弟任务是否还能收尾」与「同组取消」的差别。

| API | 并发单元 | 失败行为 |
|---|---|---|
| `asyncio.gather` | 协程/Task | 默认快速失败；可收集异常 |
| `ThreadPoolExecutor` + `as_completed` | 线程 | 异常在 `future.result()` |
| `TaskGroup` | Task | 一组内互相取消 |

```python run
import asyncio

API_ROLES = {
    "create_task": "包装协程为 Task 并调度",
    "gather": "并行等待多个 awaitable，结果按参数顺序",
    "TaskGroup": "子任务失败时取消同组其余任务",
}

def pick_api(name: str) -> str:
    return API_ROLES.get(name, "unknown")

for key in ("gather", "TaskGroup"):
    print(key, "->", pick_api(key))
print("gather 可调用", callable(asyncio.gather))
print("TaskGroup 是类", asyncio.TaskGroup.__name__ if hasattr(asyncio, "TaskGroup") else "n/a")
```

把三个 API 写成角色表，输出强调 **gather 保结果顺序**、**TaskGroup 管整组取消**。读 Agent SDK 时看到 `create_task` / `gather` 应能对应到表中语义，而不是与线程池「先完成先取」混为一谈。

## 易错点

- **gather 参数传协程对象还是 Task**：都可；若需中途取消，先 `create_task` 保留句柄。
- **忘记 `await gather(...)`**：得到的是 awaitable，不是结果元组。
- **混用阻塞库**：gather 再多个也没用，每个都在卡循环。
- **TaskGroup 外访问未完成的任务**：应在 `async with` 块结束后再 `result()`。

非法参数类型（课内可运行）：

```python run raises=TypeError
import asyncio

async def ok() -> int:
    return 1

asyncio.gather(ok(), 123)
```

## 对照

| 概念 | Python asyncio | JS | Java |
|---|---|---|---|
| 合并多个异步结果 | `asyncio.gather` | `Promise.all` | `CompletableFuture.allOf` |
| 任一失败 | 默认 reject 式传播 | `Promise.all` 拒绝 | `allOf` 异常 |
| 收集部分失败 | `return_exceptions=True` | `Promise.allSettled` | 手动组合 |
| 结构化取消 | `TaskGroup` | `AbortSignal` + `Promise.race` | `StructuredTaskScope`（预览） |
| 创建并发任务 | `asyncio.create_task` | 立即执行的 async IIFE | `executor.submit` |

## 读代码

若把 `run_once` 扩展为「同时问两个 prompt」，本地可写成：

```python fragment
async def run_parallel(a: str, b: str) -> tuple[str, str]:
    return await asyncio.gather(run_once(a), run_once(b))
```

- `run_once` 来自 `async_agent.py`，每次构造新的 `FakeAsyncClient`。
- `gather` 保证返回 `(echo:a, echo:b)` 顺序，与参数顺序一致。
- 真实 Agent 里可对多个 tool 调用 `gather`（当 SDK 提供 async 方法时）；同步 SDK 仍用线程池（18.2）。

`test_async_agent.py` 目前只测单次 `run_once`；扩展测试时可 `asyncio.run(run_parallel("x","y"))`。

写测试时，若使用 `pytest-asyncio`，装饰器 `@pytest.mark.asyncio` 会替你管理 loop，与脚本里的 `asyncio.run` 不同；读项目配置时确认 `asyncio_mode`（auto/strict），避免「测试里能 await、脚本里却要 `run`」的割裂感。

取消语义：`Task.cancel()` 在 await 点抛出 `CancelledError`；`gather` 里若需清理资源，用 `try/finally` 包裹 `await`，与同步代码的 `finally` 思维一致。

**gather vs TaskGroup 选型草稿**：

- 需要「全部结果元组，哪怕部分失败也要收集」→ `gather(..., return_exceptions=True)`。
- 需要「一组任务同生共死，一个失败则取消兄弟」→ `TaskGroup`。
- 需要限制并发度（例如最多 5 个连接）→ 信号量 `asyncio.Semaphore` 配合 `create_task`。
- 仅需顺序执行 → 普通 `for` + `await`，不必强行 `gather`。

当同事说「我们 gather 了一下」时，追问：是 `asyncio.gather` 还是线程池 `as_completed`？名词相近但运行时完全不同。

`TaskGroup` 自 Python 3.11 起进入标准库；本仓库 3.12 可直接使用，与 3.15 文档描述一致（核对日期 2026-10-18）。

`asyncio.create_task(coro)` 会把协程包装为 Task 并尽快调度；读 SDK 源码时看到 `create_task`，应联想到「已提交到 loop，尚未一定执行完毕」。

并发 tool 调用时，注意 SDK 是否要求共享 client 实例；随意每次 `new Client()` 可能失去连接复用优势。

练习 `build_echo_coros` 使用默认参数 `word=w` 绑定循环变量，避免闭包捕获经典坑。

本地实验建议：用 `asyncio.run` 包装 `gather` 两个不同 `sleep` 时间的协程，打印时间戳观察重叠执行。

阅读 `asyncio` 文档目录时，把 Task、Future、gather、TaskGroup 四页一起打开，对照记忆。

19.3 将把 HTTP 客户端放到这条并发链路的末端。

## 练习

### 练习 1：挑选 gather

实现 `pick_gather()`：返回标准库里的 `asyncio.gather` 可调用对象本身（用于类型检查或别名）。

```python exercise id=s19-l02-gather
# --- starter ---
def pick_gather():
    return None
# --- solution ---
import asyncio

def pick_gather():
    return asyncio.gather
# --- check ---
import asyncio

assert pick_gather() is asyncio.gather
```

### 练习 2：组装 awaitable 列表

实现 `build_echo_coros(words: list[str])`：对每个 `w` 定义 `async def _one(): return w` 并 **调用** 得到协程，按输入顺序放入列表（不 await）。供上层 `gather(*build_echo_coros(...))` 使用。

```python exercise id=s19-l02-build
# --- starter ---
def build_echo_coros(words: list[str]) -> list:
    return []
# --- solution ---
def build_echo_coros(words: list[str]) -> list:
    out = []
    for w in words:
        async def _one(word=w):
            return word

        out.append(_one())
    return out
# --- check ---
import inspect

cs = build_echo_coros(["a", "b"])
assert len(cs) == 2
assert all(inspect.iscoroutine(c) for c in cs)
for c in cs:
    c.close()
```


## 小结

- `gather` 并发多个协程，结果元组顺序与参数一致；注意 `return_exceptions`。
- `TaskGroup`（3.11+）在子任务失败时取消同组任务，语义更严格。
- 浏览器课内验证 API 与版本；完整并发时序请在本地 `asyncio.run` 与 pytest 中观察。
- 读 Agent 代码时：多个 async 工具调用优先考虑 `gather` 或 TaskGroup。
- TaskGroup 适合严格结构化并发；gather 更灵活。
- 课内用 `inspect` 与 API 存在性检查；时序实验在本地 `asyncio.run`。
- `return_exceptions=True` 时结果列表里可能混有异常对象，需逐项判断。
- 结构化并发让取消传播更可预测，适合有清理逻辑的 Agent 批处理。

## 延伸阅读

- [asyncio.gather](https://docs.python.org/zh-cn/3/library/asyncio-task.html#asyncio.gather)
- [TaskGroup](https://docs.python.org/zh-cn/3/library/asyncio-task.html#asyncio-taskgroup)
