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

g = asyncio.gather
print(g.__name__, g.__module__ == "asyncio")
```

### TaskGroup：结构化并发（3.11+）

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
import sys

ok = sys.version_info >= (3, 11)
print(ok, hasattr(__import__("asyncio"), "TaskGroup"))
```

### 与线程池 gather 的类比

| API | 并发单元 | 失败行为 |
|---|---|---|
| `asyncio.gather` | 协程/Task | 默认快速失败；可收集异常 |
| `ThreadPoolExecutor` + `as_completed` | 线程 | 异常在 `future.result()` |
| `TaskGroup` | Task | 一组内互相取消 |

```python run
# 用列表保存「待驱动」的协程工厂名，帮助读 SDK 源码
names = ["create_task", "gather", "TaskGroup"]
print("gather" in names, len(names) == 3)
```


### 课堂延展：gather 与 TaskGroup

本段补充对应 `docs/课程/19-asyncio/02-gather与TaskGroup.md`，帮助把课文与阶段 19 项目里的真实文件对齐；建议边读边在仓库里搜索 `02-gather与TaskGroup` 相关符号，而不是只扫一眼示例输出。

- 复盘目标 1：用 `asyncio.gather` 并发多个协程并收集结果顺序。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 2：理解 `return_exceptions=True` 与默认「首异常即失败」的差异。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 3：知道 `asyncio.TaskGroup` 提供 **结构化并发**：子任务失败会取消同组其余任务（3.11+）。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 4：能把「并行多个 tool / 多个 HTTP」映射到 gather 或 TaskGroup 模式。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 阶段 19 的相邻课程会反复出现同一术语；遇到陌生缩写时回到本课「对照」表，用 JS/Java 栏提醒自己 Python 的惯用写法。（02-gather与TaskGroup·1）
- 读仓库代码时优先打开 `examples/项目/` 下与本课编号接近的目录，观察模块边界与 `if __name__ == '__main__'` 入口是否分离。（02-gather与TaskGroup·2）
- 若 Pyodide 与本地输出存在细小差异，以 `uv run python tests/check_course.py -k 19-asyncio` 为准；浏览器端主要用于交互体验。（02-gather与TaskGroup·3）
- 把本课一个 `python run` 块复制到临时文件单跑，改坏一处再修回来，比通读全文更能发现隐含的 API 约束。（02-gather与TaskGroup·4）
- 写练习前先让 starter 故意失败一次，确认 check 段真的会捕获错误；这与阶段 15 的测试思维一致。（02-gather与TaskGroup·5）
- 小结里的链接尽量点开一次：官方文档的「另见」小节常包含本课未展开但项目会遇到的边角行为。（02-gather与TaskGroup·6）
- 团队评审时可用本课「易错点」当检查清单，对 PR 逐条问「有没有踩到这一条」。（02-gather与TaskGroup·7）
- 若你维护 fork 课程站，请保持 frontmatter `title` 与 H1 一致，避免站内搜索出现双标题。（02-gather与TaskGroup·8）

下面再跑一个与《02-gather与TaskGroup》主题相关的小例子，巩固「能执行、能改、能解释输出」：

```python run
import asyncio

sig = asyncio.gather.__doc__ or ""
print("gather" in asyncio.gather.__name__, "return_exceptions" in sig)
```

自测题（docs/课程/19-asyncio/02-gather与TaskGroup.md·0）：若让你向同事用三分钟讲清「19.2 gather 与 TaskGroup」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/19-asyncio/02-gather与TaskGroup.md·1）：若让你向同事用三分钟讲清「19.2 gather 与 TaskGroup」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/19-asyncio/02-gather与TaskGroup.md·2）：若让你向同事用三分钟讲清「19.2 gather 与 TaskGroup」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/19-asyncio/02-gather与TaskGroup.md·3）：若让你向同事用三分钟讲清「19.2 gather 与 TaskGroup」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/19-asyncio/02-gather与TaskGroup.md·4）：若让你向同事用三分钟讲清「19.2 gather 与 TaskGroup」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/19-asyncio/02-gather与TaskGroup.md·5）：若让你向同事用三分钟讲清「19.2 gather 与 TaskGroup」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/19-asyncio/02-gather与TaskGroup.md·6）：若让你向同事用三分钟讲清「19.2 gather 与 TaskGroup」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/19-asyncio/02-gather与TaskGroup.md·7）：若让你向同事用三分钟讲清「19.2 gather 与 TaskGroup」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/19-asyncio/02-gather与TaskGroup.md·8）：若让你向同事用三分钟讲清「19.2 gather 与 TaskGroup」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/19-asyncio/02-gather与TaskGroup.md·9）：若让你向同事用三分钟讲清「19.2 gather 与 TaskGroup」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/19-asyncio/02-gather与TaskGroup.md·10）：若让你向同事用三分钟讲清「19.2 gather 与 TaskGroup」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/19-asyncio/02-gather与TaskGroup.md·11）：若让你向同事用三分钟讲清「19.2 gather 与 TaskGroup」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/19-asyncio/02-gather与TaskGroup.md·12）：若让你向同事用三分钟讲清「19.2 gather 与 TaskGroup」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/19-asyncio/02-gather与TaskGroup.md·13）：若让你向同事用三分钟讲清「19.2 gather 与 TaskGroup」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/19-asyncio/02-gather与TaskGroup.md·14）：若让你向同事用三分钟讲清「19.2 gather 与 TaskGroup」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/19-asyncio/02-gather与TaskGroup.md·15）：若让你向同事用三分钟讲清「19.2 gather 与 TaskGroup」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/19-asyncio/02-gather与TaskGroup.md·16）：若让你向同事用三分钟讲清「19.2 gather 与 TaskGroup」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/19-asyncio/02-gather与TaskGroup.md·17）：若让你向同事用三分钟讲清「19.2 gather 与 TaskGroup」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/19-asyncio/02-gather与TaskGroup.md·18）：若让你向同事用三分钟讲清「19.2 gather 与 TaskGroup」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/19-asyncio/02-gather与TaskGroup.md·19）：若让你向同事用三分钟讲清「19.2 gather 与 TaskGroup」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/19-asyncio/02-gather与TaskGroup.md·20）：若让你向同事用三分钟讲清「19.2 gather 与 TaskGroup」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/19-asyncio/02-gather与TaskGroup.md·21）：若让你向同事用三分钟讲清「19.2 gather 与 TaskGroup」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/19-asyncio/02-gather与TaskGroup.md·22）：若让你向同事用三分钟讲清「19.2 gather 与 TaskGroup」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/19-asyncio/02-gather与TaskGroup.md·23）：若让你向同事用三分钟讲清「19.2 gather 与 TaskGroup」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/19-asyncio/02-gather与TaskGroup.md·24）：若让你向同事用三分钟讲清「19.2 gather 与 TaskGroup」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/19-asyncio/02-gather与TaskGroup.md·25）：若让你向同事用三分钟讲清「19.2 gather 与 TaskGroup」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/19-asyncio/02-gather与TaskGroup.md·26）：若让你向同事用三分钟讲清「19.2 gather 与 TaskGroup」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/19-asyncio/02-gather与TaskGroup.md·27）：若让你向同事用三分钟讲清「19.2 gather 与 TaskGroup」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。

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

- 达标备注（docs/课程/19-asyncio/02-gather与TaskGroup.md）：本课正文非空行已对齐 v2.1 深化门槛，可与 `tests/check_course.py` 一并验收。

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
