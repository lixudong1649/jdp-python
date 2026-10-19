---
title: 18.3 free-threaded 现状
---

# 18.3 free-threaded 现状

> 前置：18.1 threading 与 GIL · 约 30 分钟 · 官方对应：[What's New 3.14](https://docs.python.org/zh-cn/3/whatsnew/3.14.html)、[PEP 703](https://peps.python.org/pep-0703/) · 核对日期 2026-10-18（free-threaded 构建自 3.14 起官方提供；默认发行版仍多为 GIL；Python 3.10 已 EOL）

## 目标

- 知道 **free-threaded（无 GIL）** CPython 从 3.14 起可作为官方实验/可选构建，而非默认唯一行为。
- 理解对扩展模块、打包、部署的影响：ABI 与 wheel 标签仍在演进。
- 在本课程固定 **3.12** 的前提下，如何写「对未来友好」的并发代码。
- 避免把博客 标题里的「Python 去掉 GIL」误读成「你 pip 装的版本已无锁」。

## 核心概念

### 默认 CPython 仍有 GIL

绝大多数用户通过 python.org 或系统包管理器安装的是 **带 GIL** 的解释器。多线程 CPU 密集行为与 18.1 描述一致。

课内用版本元信息确认当前解释器（浏览器与本地均可）：

```python run
import sys

vi = sys.version_info
version_tag = f"{vi.major}.{vi.minor}.{vi.micro}"
is_314_plus = vi >= (3, 14)
mentions_ft = "free-threaded" in sys.version.lower()
print("解释器版本", version_tag)
print("版本元组>=3.14", is_314_plus)
print("version 字符串含 free-threaded", mentions_ft)
print("默认 wheel 仍多为 GIL", not mentions_ft or "需读发行说明")
```

输出里的版本号描述**当前课内解释器**，不等于你已安装 nogil 构建。`mentions_ft` 为真才说明字符串里标了 free-threaded；多数 pip 包仍是带 GIL 的 CPython，选型时以 `python -VV` 与官方发行说明为准。

### free-threaded 改变了什么

在 nogil 构建上，多个线程可并行执行 Python 字节码（仍受 CPU 核数限制）。这会让：

- **CPU 密集多线程** 有可能获得接近线性的加速（工作负载与实现相关）。
- **C 扩展** 必须明确声明是否支持 free-threaded；旧扩展可能崩溃或回退到 GIL。

因此生产迁移是「重新测、重新打包、重新选依赖」，不是改一行配置就完事。

### 课程与项目的务实策略（2026-10-18）

| 层级 | 建议 |
|---|---|
| 本仓库 `pyproject` 固定 3.12 | 继续按 GIL 模型写线程/进程选型 |
| 新库 | 避免依赖「GIL 保护下的偶然线程安全」 |
| 性能关键路径 | 先算法与数据结构（阶段 20），再考虑进程池或原生扩展 |
| 跟踪官方 | 关注 3.14+ release notes 与 PEP 703 状态 |

```python local
# 编写与未来 free-threaded 兼容的计数：仍用 Lock，不依赖「整段字节码原子」
import threading

class Counter:
    def __init__(self) -> None:
        self._n = 0
        self._lock = threading.Lock()

    def inc(self) -> int:
        with self._lock:
            self._n += 1
            return self._n

c = Counter()
print(c.inc(), c.inc())
```

检测当前解释器是否暴露 GIL 状态 API（3.13+ 提供 `sys._is_gil_enabled()`；课内环境可能为 3.12 或 3.14）：

```python run
import sys

vi = sys.version_info
has_probe = hasattr(sys, "_is_gil_enabled")
print(vi.major, vi.minor, has_probe)
if has_probe:
    print("gil_enabled", sys._is_gil_enabled())
else:
    print("gil_enabled", "n/a")
```

即使未来无 GIL，显式锁仍保护 **逻辑不变量**；只是 GIL 不再替你掩盖所有竞态。

对库作者而言，文档里应写明「线程安全等级」：纯函数、不可变返回值、需外部锁、或仅主线程调用。free-threaded 时代，「因为 GIL 所以勉强安全」的注释需要重写为明确契约。

### 与 asyncio、多进程的关系

free-threaded **不替代** asyncio：高并发 I/O 仍常用事件循环。也不废除 `multiprocessing`：进程隔离仍是重 CPU 与故障隔离手段。

```python run
def shared_counter_steps(steps: int) -> tuple[int, int]:
    total = 0
    for _ in range(steps):
        total += 1
    return total, total

def explain_race(total: int, expected: int) -> str:
    if total == expected:
        return "单线程结果一致"
    return "多线程无锁可能丢增量"

a, b = shared_counter_steps(5)
msg = explain_race(a, 5)
print("单线程递增", a, "期望", 5)
print("诊断", msg)
print("free-threaded 后多线程 CPU 可能并行", "仍要显式锁")
print("与 asyncio 无关", "I/O 仍用事件循环")
```

这段用纯 Python 递增说明：**无论是否有 GIL**，多个线程同时改同一整数都需要锁保护逻辑不变量。free-threaded 让 CPU 字节码可能真并行，但不会替你做同步；高并发 I/O 仍应走 asyncio（阶段 19），而不是指望去掉 GIL 就万能。

阅读官方 What's New 时，请区分 **「构建选项」** 与 **「默认 wheel」**：PyPI 上名为 `cp312` 的轮子通常仍假设 GIL；nogil 标签与包名规则以 [packaging 讨论](https://packaging.python.org/) 与 3.14 文档为准，不要凭记忆猜标签字符串。

若本机安装 **free-threaded** 构建（可执行文件常带 `t` 后缀，如 `python3.14t`），可在本地确认：

```python local
import sys

print(sys.executable)
if hasattr(sys, "_is_gil_enabled"):
    print("gil_enabled", sys._is_gil_enabled())
else:
    print("no _is_gil_enabled on this build")
```

扩展模块需在文档中声明是否支持 free-threaded；混用旧 wheel 可能导致导入失败或运行时崩溃，升级前用依赖清单逐项核对。

## 易错点

- **把 3.14 新闻当成「生产默认已无 GIL」**：以你实际安装的 wheel 与 `python -VV` 为准。
- **忽略 C 扩展**：NumPy、pandas 等需等待上游声明支持；混装错误 wheel 会难以排查。
- **以为 free-threaded 消灭数据竞争**：共享可变状态仍要锁、队列或不可变结构。
- **继续推荐「多线程算质数」作为通用方案**：无 GIL 后可能有效，但仍受核数与任务划分限制；先测量。

错误版本假设会导致错误的安全感：

```python run raises=AssertionError
def migration_checklist() -> dict[str, str]:
    return {
        "wheels": "核对扩展是否声明 nogil 兼容",
        "bench": "用 timeit 重测 CPU 与 I/O 路径",
    }

checklist = migration_checklist()
print("升级前条目数", len(checklist))
print("第一项", checklist["wheels"])
# 错误假设：3.14 起官方已有可选 free-threaded 构建，不能再写「永远 <3.14 无 nogil」
policy = (3, 14)
assert policy < (3, 14), "官方已提供 free-threaded 选项，请读 18.3"
```

清单打印说明迁移要先查 wheel 与压测；随后的断言故意用过时前提 `(3,14) < (3,14)` 触发 `AssertionError`，提醒文档与口头结论不能停留在「3.14 之前绝无 nogil」的旧说法。

## 对照

| 概念 | Python（带 GIL 默认） | Python（free-threaded 可选） | JS | Java |
|---|---|---|---|---|
| 多线程 CPU 字节码 | 基本串行 | 可并行（受核数限制） | 单线程为主 | 真并行 |
| 内存模型 | GIL 简化部分竞态 | 需正规同步 | 隔离 | JMM + 同步原语 |
| 扩展模块 | 传统 ABI | 需 nogil 兼容声明 | N/A | JNI 规则 |
| 发布形态 | 标准 wheel | 额外标签/构建 | npm 包 | JAR |

## 读代码

阶段 18 的 `downloader.py` **没有** 依赖 free-threaded：它假设常规 GIL + 线程阻塞 I/O。若未来在 nogil 解释器上运行，同一源码通常仍能工作，但：

- 不应再假设「CPython 整数运算因 GIL 而免于所有竞态」；本项目已在 18.1 用 `Lock` 讨论共享状态。
- 若把 `fetch` 换成 CPU 密集且加大 `workers`，在 nogil 上可能看到不同缩放曲线，必须用 `timeit`（阶段 20）实测。

`test_downloader.py` 在任意 3.12+ GIL 构建上断言行为；升级解释器时先跑：

```bash
cd examples/项目/18-并发下载模拟 && uv run pytest -q
```

团队选型时可简单记录一张表：解释器版本、是否 free-threaded、关键 C 扩展版本、压测脚本链接——日后升级 3.14+ 时可复现对比，而不是重新猜瓶颈。

### 学习检查（自测）

你能口头回答下面三点即可进入阶段 19：① 默认 pip 装的 CPython 是否一定无 GIL；② 为何 `downloader` 仍用线程池；③ 共享计数为何需要 `Lock` 而不是依赖 GIL 偶然安全。

社区文章若写「Python 多线程完全没用」，应加上前提：**CPU 密集字节码** vs **I/O 等待**。作为工程师，你的职责是把 workload 分类，而不是背诵绝对结论。

**时间线备忘（核对日期 2026-10-18）**：

- Python 3.10 已 EOL，新项目不应再以其为上限。
- 本仓库教学环境固定 3.12，文档叙述同时对照稳定版 3.15。
- 3.14 起官方提供 free-threaded **可选**构建；是否启用取决于你安装的发行物，而非仅看次版本号。
- 扩展模块作者需单独声明 nogil 兼容；业务方升级前应用自家压测与依赖清单验证。
- 无论是否有 GIL，应用层共享状态仍建议显式同步原语。

本课不要求你立刻安装 free-threaded 构建；重点是 **读懂发行说明**，避免在团队沟通中混淆「官方支持可选构建」与「默认 wheel 已无 GIL」。

进入阶段 19 时，记住：asyncio 解决的是 **协作式 I/O 并发**，与 nogil 线程并行是不同维度，可以组合但不应混为一谈。

若你维护 C 扩展，请直接阅读 PEP 703 中的「扩展模块作者」章节，而不是只读科普博客摘要。

默认学习路径仍以 GIL 心智模型为主；nogil 作为升级检查项即可。

## 练习

### 练习 1：版本元组比较

实现 `supports_modern_concurrency(major, minor) -> bool`：当 `(major, minor) >= (3, 12)` 返回 `True`（本课程最低版本），否则 `False`。

```python exercise id=s18-l03-ft
# --- starter ---
def supports_modern_concurrency(major: int, minor: int) -> bool:
    return False
# --- solution ---
def supports_modern_concurrency(major: int, minor: int) -> bool:
    return (major, minor) >= (3, 12)
# --- check ---
assert supports_modern_concurrency(3, 12) is True
assert supports_modern_concurrency(3, 11) is False
```

### 练习 2：GIL 探测摘要

实现 `gil_probe_label() -> str`：若 `sys` 提供 `_is_gil_enabled()`，返回 `"enabled"` 或 `"disabled"`（按布尔值）；否则返回 `"unknown"`。不要捕获属性错误以外的异常。

```python exercise id=s18-l03-gilprobe
# --- starter ---
import sys

def gil_probe_label() -> str:
    return "maybe"
# --- solution ---
import sys

def gil_probe_label() -> str:
    probe = getattr(sys, "_is_gil_enabled", None)
    if probe is None:
        return "unknown"
    return "enabled" if probe() else "disabled"
# --- check ---
import sys

label = gil_probe_label()
if hasattr(sys, "_is_gil_enabled"):
    assert label in ("enabled", "disabled")
else:
    assert label == "unknown"
```

### 练习 3：带锁的递增器

补全 `SafeBox`：`increment` 在锁内把 `self.value` 加 1 并返回新值。

```python local exercise id=s18-l03-safebox
# --- starter ---
import threading

class SafeBox:
    def __init__(self) -> None:
        self.value = 0
        self._lock = threading.Lock()

    def increment(self) -> int:
        return self.value
# --- solution ---
import threading

class SafeBox:
    def __init__(self) -> None:
        self.value = 0
        self._lock = threading.Lock()

    def increment(self) -> int:
        with self._lock:
            self.value += 1
            return self.value
# --- check ---
b = SafeBox()
assert b.increment() == 1
assert b.increment() == 2
```


## 小结

- 3.14 起官方提供 free-threaded 可选构建；默认生态仍以 GIL 为主。
- 扩展模块与 wheel 兼容是迁移关键；不能只看新闻标题。
- 写库与业务时继续用锁/队列保护不变量；本课程环境固定 3.12。
- 性能与并发选型以实测为准，阶段 20 会系统讲测量与优化。
- 升级解释器时先跑全量 pytest 与扩展依赖清单，再考虑开启实验性 nogil 构建做对比实验。
- 新闻标题里的「去掉 GIL」不等于你 `python3` 二进制已是 nogil。
- 业务代码仍按显式锁与清晰并发模型编写，兼容性最好。

## 延伸阅读

- [What's New In Python 3.14](https://docs.python.org/zh-cn/3/whatsnew/3.14.html)
- [PEP 703 – Making the Global Interpreter Lock Optional in CPython](https://peps.python.org/pep-0703/)
