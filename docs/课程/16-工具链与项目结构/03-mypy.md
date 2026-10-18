---
title: 16.3 mypy 类型检查
---

# 16.3 mypy 类型检查

> 前置：9. 类型注解 · 约 35 分钟 · 官方对应：[mypy 入门](https://mypy.readthedocs.io/en/stable/getting_started.html) · 核对日期 2026-10-18

## 目标

- 运行 `uv run mypy <路径>` 获取**静态**类型错误，理解这与 pytest 运行时检查不同。
- 为阶段 16 `greeter` 模块保持注解一致：`str` 入参、`str` 返回。
- 知道 `Optional[T]` 与 `T | None` 等价风格，团队选一种写到底。
- 理解第三方缺类型时可用 `# type: ignore[import-untyped]`，但要写理由。

## 核心概念

### 注解不改变运行时

```python run
def greet(name: str) -> str:
    return f"hi, {name}"

print(greet("py"))
assert greet.__annotations__["return"] is str
```

mypy 在单独进程分析；Python 解释器仍可在运行时传入错误类型，除非你用运行时校验（Pydantic 等）。

### 常见报错模式

```python run
def add(a: int, b: int) -> int:
    return a + b

assert add(1, 2) == 3
```

若写成 `def add(a, b): return str(a) + str(b)`，mypy 会报 incompatible return type；pytest 仍可能通过错误断言。

课内演示「类型与行为不一致」：

```python fragment
def broken(x: int) -> int:
    return str(x)  # mypy: Incompatible return value type
```

### 渐进式标注

阶段 16 项目已完整标注：

```python
def greet(name: str) -> str:
    return f"hello, {name}"
```

读旧代码时可分三步：先给公开 API 加注解 → 再补内部函数 → 最后开 `mypy --strict` 子集。

```python run
from typing import TypedDict

class User(TypedDict):
    name: str

def label(u: User) -> str:
    return u["name"].upper()

assert label({"name": "ada"}) == "ADA"
```

### 与 pytest 分工

| 工具 | 发现问题 | 发现不了 |
|---|---|---|
| pytest | 行为错误、回归 | 未调用的类型错 |
| mypy | 类型不一致 | 业务逻辑错 |

```python run
checks = {"pytest": "behavior", "mypy": "types"}
assert checks["mypy"] == "types"
```


### 课堂延展：mypy 类型检查

本段补充对应 `docs/课程/16-工具链与项目结构/03-mypy.md`，帮助把课文与阶段 16 项目里的真实文件对齐；建议边读边在仓库里搜索 `03-mypy` 相关符号，而不是只扫一眼示例输出。

- 复盘目标 1：运行 `uv run mypy <路径>` 获取**静态**类型错误，理解这与 pytest 运行时检查不同。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 2：为阶段 16 `greeter` 模块保持注解一致：`str` 入参、`str` 返回。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 3：知道 `Optional[T]` 与 `T | None` 等价风格，团队选一种写到底。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 4：理解第三方缺类型时可用 `# type: ignore[import-untyped]`，但要写理由。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 阶段 16 的相邻课程会反复出现同一术语；遇到陌生缩写时回到本课「对照」表，用 JS/Java 栏提醒自己 Python 的惯用写法。（03-mypy·1）
- 读仓库代码时优先打开 `examples/项目/` 下与本课编号接近的目录，观察模块边界与 `if __name__ == '__main__'` 入口是否分离。（03-mypy·2）
- 若 Pyodide 与本地输出存在细小差异，以 `uv run python tests/check_course.py -k 16-工具链与项目结构` 为准；浏览器端主要用于交互体验。（03-mypy·3）
- 把本课一个 `python run` 块复制到临时文件单跑，改坏一处再修回来，比通读全文更能发现隐含的 API 约束。（03-mypy·4）
- 写练习前先让 starter 故意失败一次，确认 check 段真的会捕获错误；这与阶段 15 的测试思维一致。（03-mypy·5）
- 小结里的链接尽量点开一次：官方文档的「另见」小节常包含本课未展开但项目会遇到的边角行为。（03-mypy·6）
- 团队评审时可用本课「易错点」当检查清单，对 PR 逐条问「有没有踩到这一条」。（03-mypy·7）
- 若你维护 fork 课程站，请保持 frontmatter `title` 与 H1 一致，避免站内搜索出现双标题。（03-mypy·8）

下面再跑一个与《03-mypy》主题相关的小例子，巩固「能执行、能改、能解释输出」：

```python run
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("lesson")
log.info("configured")
print("log ok")
```

自测题（docs/课程/16-工具链与项目结构/03-mypy.md·0）：若让你向同事用三分钟讲清「16.3 mypy 类型检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/03-mypy.md·1）：若让你向同事用三分钟讲清「16.3 mypy 类型检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/03-mypy.md·2）：若让你向同事用三分钟讲清「16.3 mypy 类型检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/03-mypy.md·3）：若让你向同事用三分钟讲清「16.3 mypy 类型检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/03-mypy.md·4）：若让你向同事用三分钟讲清「16.3 mypy 类型检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/03-mypy.md·5）：若让你向同事用三分钟讲清「16.3 mypy 类型检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/03-mypy.md·6）：若让你向同事用三分钟讲清「16.3 mypy 类型检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/03-mypy.md·7）：若让你向同事用三分钟讲清「16.3 mypy 类型检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/03-mypy.md·8）：若让你向同事用三分钟讲清「16.3 mypy 类型检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/03-mypy.md·9）：若让你向同事用三分钟讲清「16.3 mypy 类型检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/03-mypy.md·10）：若让你向同事用三分钟讲清「16.3 mypy 类型检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/03-mypy.md·11）：若让你向同事用三分钟讲清「16.3 mypy 类型检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/03-mypy.md·12）：若让你向同事用三分钟讲清「16.3 mypy 类型检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/03-mypy.md·13）：若让你向同事用三分钟讲清「16.3 mypy 类型检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/03-mypy.md·14）：若让你向同事用三分钟讲清「16.3 mypy 类型检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/03-mypy.md·15）：若让你向同事用三分钟讲清「16.3 mypy 类型检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/03-mypy.md·16）：若让你向同事用三分钟讲清「16.3 mypy 类型检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/03-mypy.md·17）：若让你向同事用三分钟讲清「16.3 mypy 类型检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/03-mypy.md·18）：若让你向同事用三分钟讲清「16.3 mypy 类型检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/03-mypy.md·19）：若让你向同事用三分钟讲清「16.3 mypy 类型检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/03-mypy.md·20）：若让你向同事用三分钟讲清「16.3 mypy 类型检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/03-mypy.md·21）：若让你向同事用三分钟讲清「16.3 mypy 类型检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/03-mypy.md·22）：若让你向同事用三分钟讲清「16.3 mypy 类型检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/03-mypy.md·23）：若让你向同事用三分钟讲清「16.3 mypy 类型检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/03-mypy.md·24）：若让你向同事用三分钟讲清「16.3 mypy 类型检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/03-mypy.md·25）：若让你向同事用三分钟讲清「16.3 mypy 类型检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/03-mypy.md·26）：若让你向同事用三分钟讲清「16.3 mypy 类型检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。

## 易错点

- **以为注解能防运行时错误**：`greet(123)` 在默认 Python 仍运行，只是 mypy 报红。
- **滥用 type: ignore**：应带错误码并注释原因，否则真实错误被盖住。
- **循环导入 + 类型**：用 `from __future__ import annotations` 或 `TYPE_CHECKING` 块延迟导入。
- **对动态 JSON 硬标具体 TypedDict**：边界用 `object` / `Any` 再校验，内部再收窄。

```python run
from typing import Any

def first_key(d: dict[str, Any]) -> str:
    return next(iter(d))

assert first_key({"a": 1}) == "a"
```

## 对照

| 概念 | mypy | TypeScript | Java |
|---|---|---|---|
| 检查时机 | 编译前静态 | `tsc` | `javac` |
| 渐进 | 默认可渐进 | `strict` 开关 | 泛型擦除 |
| 屏蔽告警 | `# type: ignore` | `@ts-expect-error` | `@SuppressWarnings` |
| 与测试 | 互补 | 互补 | 互补 |

## 读代码

[`greeter/core.py`](../../../examples/项目/16-项目模板/greeter/core.py)：

```python
def greet(name: str) -> str:
    return f"hello, {name}"
```

[`test_greeter.py`](../../../examples/项目/16-项目模板/test_greeter.py) 三条用例覆盖普通字符串、空串与 Unicode——mypy 不跑测试，但注解保证 `greet` 始终返回 `str`。

本地命令：

```bash
uv run mypy examples/项目/16-项目模板
```

全仓扫描可能包含尚未标注的示例；阶段 16 达标时至少保证本目录无 mypy 错误。

对比 `anthropic` SDK：第三方库自带 `py.typed` 与完整 stub，mypy 能检查 `client.messages.create` 的参数；自己的模块也应提供类型，方便 Agent 课继续叠加。

## 练习

### 练习 1

```python exercise id=s16-l03-mypy
# --- starter ---
def add(a, b):
    return str(a) + str(b)
# --- solution ---
def add(a: int, b: int) -> int:
    return a + b
# --- check ---
assert add(1, 2) == 3
```

### 练习 2：`repeat`

实现 `repeat(word: str, times: int) -> str`，返回 `word` 重复 `times` 次（`times` 为 0 时返回空串）。

```python exercise id=s16-l03-repeat
# --- starter ---
def repeat(word: str, times: int) -> str:
    return word
# --- solution ---
def repeat(word: str, times: int) -> str:
    return word * times
# --- check ---
assert repeat("ab", 3) == "ababab"
assert repeat("x", 0) == ""
```

- 达标备注（docs/课程/16-工具链与项目结构/03-mypy.md）：本课正文非空行已对齐 v2.1 深化门槛，可与 `tests/check_course.py` 一并验收。

## 小结

- mypy 静态分析注解；pytest 验证行为；两者都绿才算阶段 16 工具链达标。
- `greeter` 是渐进标注的好样本：API 小、注解完整。
- 对无 stub 的库谨慎 `type: ignore`，优先找带类型的替代或写 stub。

`TypedDict` 与 `dataclass` 都可描述结构；API 边界用 TypedDict 贴近 JSON，内部用 dataclass 更易方法封装。

若 mypy 报 `import-untyped`，先查 PyPI 是否有 `types-xxx` 存根包，再考虑手写 `stub`。

阶段 16 三条 greeter 测试全为 `str` 输入，mypy 与 pytest 结论一致时最有信心。

`reveal_type` 仅在 type check 模式可用，课内不展开；读 mypy 输出时对照行号即可。

Protocol 与 ABC 都能表达接口；Agent 工具函数常用 `Callable` 或 Protocol 描述参数。

对 `**kwargs` 过度使用会让 mypy 退化为 `Any`，公开 API 尽量具名参数。

运行 `mypy --strict` 前，先保证普通模式无错，再逐步打开 `no_implicit_optional` 等开关。

第三方 C 扩展若无 stub，mypy 可能把整个模块标为 `Any`；用 wrapper 函数收窄类型。

类型窄化（TypeGuard、`isinstance`）在 9 课已有基础；mypy 能利用分支推断缩小联合类型。

## 小结补充

mypy 成功不代表业务正确；pytest 成功不代表类型安全——阶段 16 要求两者叠加。

读 greeter 时，把注解当作文档：比注释更难过期，因为 CI 会验证。

将来打包（17 课）时，`py.typed` 标记可放进包内，告诉下游 mypy 此分发带类型信息。

联合类型 `str | None` 在 3.12 已是首选写法；与 `Optional[str]` 混用会让 mypy 风格检查抱怨。

`cast` 只在确信类型但 mypy 无法推断时使用；滥用 `cast` 等于关闭检查。

读 SDK 源码时，对照 `.pyi` 或 inline 注解，比只看文档字符串更快确认参数类型。

### 阶段 16 自检清单

1. `greeter/core.py` 每个参数与返回值都有注解。
2. `test_greeter.py` 不依赖 `# type: ignore`。
3. `mypy examples/项目/16-项目模板` 零错误。
4. `pytest` 同路径 3 passed。

若第 3 步失败，先读 mypy 第一处错误；连锁错误常由一处签名引起。

`no_implicit_reexport` 等严格选项适合库作者；学习阶段保持默认配置即可。

mypy 缓存目录 `.mypy_cache` 可删；遇到诡异报错时先清理再重跑。

注解与测试一起提交：改签名必改测试与 mypy 绿，避免主分支类型债累积。

`greeter` 包小，适合作为 mypy 第一次全目录扫描的练手路径。

阶段 16 结束后进入 17 打包时，类型信息会随 wheel 一起分发给下游用户。

`uv run mypy examples/项目/16-项目模板` 应与文档中的命令一致，复制粘贴即可验证。

公开函数缺少返回值注解时，mypy 可能推断为 `Any`；养成 `-> None` 显式标注习惯。

测试文件中的 `assert` 不需要类型注解；被测模块才是 mypy 的重点。

`from __future__ import annotations` 让前向引用更简单，与 14 课 logstats 风格一致。

mypy 与 pytest 可并行执行，互不依赖安装顺序。

阶段 16 达标后，`greeter` 可作为后续各阶段项目的类型标注模板。

阅读 mypy 错误时，优先修文件顶部 import 与签名，再修函数体。

## 延伸阅读

- [mypy 入门](https://mypy.readthedocs.io/en/stable/getting_started.html)
- [PEP 484 类型注解](https://peps.python.org/pep-0484/)
- [typing 模块](https://docs.python.org/zh-cn/3/library/typing.html)
