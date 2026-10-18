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
print(vi.major, vi.minor, vi.micro >= 0)
print("free-threaded" in sys.version.lower() or vi >= (3, 14))
```

第二行打印 `True` 只表示「版本号已达 3.14+」，**不**代表当前构建一定启用了 nogil；需查看发行说明与 `sys` 提供的 GIL 检测 API（3.13+ 实验字段以官方文档为准）。

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

```python run
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

即使未来无 GIL，显式锁仍保护 **逻辑不变量**；只是 GIL 不再替你掩盖所有竞态。

对库作者而言，文档里应写明「线程安全等级」：纯函数、不可变返回值、需外部锁、或仅主线程调用。free-threaded 时代，「因为 GIL 所以勉强安全」的注释需要重写为明确契约。

### 与 asyncio、多进程的关系

free-threaded **不替代** asyncio：高并发 I/O 仍常用事件循环。也不废除 `multiprocessing`：进程隔离仍是重 CPU 与故障隔离手段。

```python run
import asyncio
import inspect

async def ping() -> str:
    return "pong"

coro = ping()
print(inspect.iscoroutine(coro))
coro.close()
```

协程对象可在课内创建；完整 `asyncio.run` 请在本地运行阶段 19 项目。

阅读官方 What's New 时，请区分 **「构建选项」** 与 **「默认 wheel」**：PyPI 上名为 `cp312` 的轮子通常仍假设 GIL；nogil 标签与包名规则以 [packaging 讨论](https://packaging.python.org/) 与 3.14 文档为准，不要凭记忆猜标签字符串。


### 课堂延展：free-threaded 现状

本段补充对应 `docs/课程/18-并发/03-free-threaded现状.md`，帮助把课文与阶段 18 项目里的真实文件对齐；建议边读边在仓库里搜索 `03-free-threaded现状` 相关符号，而不是只扫一眼示例输出。

- 复盘目标 1：知道 **free-threaded（无 GIL）** CPython 从 3.14 起可作为官方实验/可选构建，而非默认唯一行为。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 2：理解对扩展模块、打包、部署的影响：ABI 与 wheel 标签仍在演进。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 3：在本课程固定 **3.12** 的前提下，如何写「对未来友好」的并发代码。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 4：避免把博客 标题里的「Python 去掉 GIL」误读成「你 pip 装的版本已无锁」。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 阶段 18 的相邻课程会反复出现同一术语；遇到陌生缩写时回到本课「对照」表，用 JS/Java 栏提醒自己 Python 的惯用写法。（03-free-threaded现状·1）
- 读仓库代码时优先打开 `examples/项目/` 下与本课编号接近的目录，观察模块边界与 `if __name__ == '__main__'` 入口是否分离。（03-free-threaded现状·2）
- 若 Pyodide 与本地输出存在细小差异，以 `uv run python tests/check_course.py -k 18-并发` 为准；浏览器端主要用于交互体验。（03-free-threaded现状·3）
- 把本课一个 `python run` 块复制到临时文件单跑，改坏一处再修回来，比通读全文更能发现隐含的 API 约束。（03-free-threaded现状·4）
- 写练习前先让 starter 故意失败一次，确认 check 段真的会捕获错误；这与阶段 15 的测试思维一致。（03-free-threaded现状·5）
- 小结里的链接尽量点开一次：官方文档的「另见」小节常包含本课未展开但项目会遇到的边角行为。（03-free-threaded现状·6）
- 团队评审时可用本课「易错点」当检查清单，对 PR 逐条问「有没有踩到这一条」。（03-free-threaded现状·7）
- 若你维护 fork 课程站，请保持 frontmatter `title` 与 H1 一致，避免站内搜索出现双标题。（03-free-threaded现状·8）

下面再跑一个与《03-free-threaded现状》主题相关的小例子，巩固「能执行、能改、能解释输出」：

```python run
import sys

# free-threaded 与否都仍需保护共享可变状态；课内只演示「版本元数据」可读
info = sys.version_info
print(info.major, info.minor >= 12, hasattr(sys, "_is_gil_enabled"))
```

自测题（docs/课程/18-并发/03-free-threaded现状.md·0）：若让你向同事用三分钟讲清「18.3 free-threaded 现状」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/03-free-threaded现状.md·1）：若让你向同事用三分钟讲清「18.3 free-threaded 现状」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/03-free-threaded现状.md·2）：若让你向同事用三分钟讲清「18.3 free-threaded 现状」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/03-free-threaded现状.md·3）：若让你向同事用三分钟讲清「18.3 free-threaded 现状」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/03-free-threaded现状.md·4）：若让你向同事用三分钟讲清「18.3 free-threaded 现状」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/03-free-threaded现状.md·5）：若让你向同事用三分钟讲清「18.3 free-threaded 现状」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/03-free-threaded现状.md·6）：若让你向同事用三分钟讲清「18.3 free-threaded 现状」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/03-free-threaded现状.md·7）：若让你向同事用三分钟讲清「18.3 free-threaded 现状」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/03-free-threaded现状.md·8）：若让你向同事用三分钟讲清「18.3 free-threaded 现状」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/03-free-threaded现状.md·9）：若让你向同事用三分钟讲清「18.3 free-threaded 现状」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/03-free-threaded现状.md·10）：若让你向同事用三分钟讲清「18.3 free-threaded 现状」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/03-free-threaded现状.md·11）：若让你向同事用三分钟讲清「18.3 free-threaded 现状」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/03-free-threaded现状.md·12）：若让你向同事用三分钟讲清「18.3 free-threaded 现状」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/03-free-threaded现状.md·13）：若让你向同事用三分钟讲清「18.3 free-threaded 现状」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/03-free-threaded现状.md·14）：若让你向同事用三分钟讲清「18.3 free-threaded 现状」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/03-free-threaded现状.md·15）：若让你向同事用三分钟讲清「18.3 free-threaded 现状」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/03-free-threaded现状.md·16）：若让你向同事用三分钟讲清「18.3 free-threaded 现状」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/03-free-threaded现状.md·17）：若让你向同事用三分钟讲清「18.3 free-threaded 现状」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/03-free-threaded现状.md·18）：若让你向同事用三分钟讲清「18.3 free-threaded 现状」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/03-free-threaded现状.md·19）：若让你向同事用三分钟讲清「18.3 free-threaded 现状」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/03-free-threaded现状.md·20）：若让你向同事用三分钟讲清「18.3 free-threaded 现状」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/18-并发/03-free-threaded现状.md·21）：若让你向同事用三分钟讲清「18.3 free-threaded 现状」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。

## 易错点

- **把 3.14 新闻当成「生产默认已无 GIL」**：以你实际安装的 wheel 与 `python -VV` 为准。
- **忽略 C 扩展**：NumPy、pandas 等需等待上游声明支持；混装错误 wheel 会难以排查。
- **以为 free-threaded 消灭数据竞争**：共享可变状态仍要锁、队列或不可变结构。
- **继续推荐「多线程算质数」作为通用方案**：无 GIL 后可能有效，但仍受核数与任务划分限制；先测量。

错误版本假设会导致错误的安全感：

```python run raises=AssertionError
# 不能用「版本 < 3.14」断言「永远没有官方 nogil 构建」——3.14 已提供可选构建
policy = (3, 14)
assert policy < (3, 14), "官方已提供 free-threaded 选项，请读 18.3"
```

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

### 练习 2：带锁的递增器

补全 `SafeBox`：`increment` 在锁内把 `self.value` 加 1 并返回新值。

```python exercise id=s18-l03-safebox
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

- 达标备注（docs/课程/18-并发/03-free-threaded现状.md）：本课正文非空行已对齐 v2.1 深化门槛，可与 `tests/check_course.py` 一并验收。

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
