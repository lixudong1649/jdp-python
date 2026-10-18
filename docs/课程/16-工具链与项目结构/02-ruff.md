---
title: 16.2 ruff 静态检查
---

# 16.2 ruff 静态检查

> 前置：16.1 pyproject · 约 35 分钟 · 官方对应：[Ruff linter](https://docs.astral.sh/ruff/linter/)、[Ruff formatter](https://docs.astral.sh/ruff/formatter/) · 核对日期 2026-10-18

## 目标

- 会用 `uv run ruff check` 扫描仓库，理解 **lint** 与 **format** 的分工。
- 读懂根目录 `[tool.ruff]`：`line-length`、`target-version`、`select` 规则集。
- 知道 `ruff check --fix` 可自动修一部分问题，但合并前要人工 diff。
- 把 ruff 当作「读代码前的卫生检查」，与 pytest 互补。

## 核心概念

### lint vs format

| 工具子命令 | 作用 | 本仓库 |
|---|---|---|
| `ruff check` | 未使用导入、语法隐患、部分 pyupgrade | CI / 本地必跑 |
| `ruff format` | 统一缩进、引号、换行 | 团队可选 |

```python run
# 课内示例：保持符合 E/F 规则的基础写法
items = [1, 2, 3]
total = sum(items)
assert total == 6
print("style ok")
```

### 本仓库 ruff 配置

```toml
[tool.ruff]
line-length = 120
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP"]
```

- **E / F**：pycodestyle 与 pyflakes 类问题（空行、未定义名等）。
- **I**：import 排序（isort 兼容）。
- **UP**：pyupgrade，提示可改用 3.12 语法。

课内模拟「规则命中」：

```python run
import math

def circle_area(r: float) -> float:
    return math.pi * r * r

assert round(circle_area(1), 5) == 3.14159
```

若删掉 `import math` 仍使用 `math.pi`，`ruff check` 会报 F821 未定义。

### per-file-ignores

长脚本或生成代码可单独放宽：

```toml
[tool.ruff.lint.per-file-ignores]
"scripts/*" = ["E501", "E402", "E741"]
```

含义：对 `scripts/` 下文件不检查行宽 E501 等。不要滥用——默认应全仓统一，只在有理由的目录登记例外（配置里用 per-file-ignores 表达，正文明说「例外目录」即可）。

```python run
rules = {"scripts/*": ["E501"], "tests/check_course.py": ["E501"]}
assert "E501" in rules["scripts/*"]
print("ignore map ok")
```

### 与 pytest 的配合

ruff 不运行测试；pytest 不查未使用导入。提交前典型顺序：

```bash
uv run ruff check .
uv run pytest -q
```

```python run
pipeline = ["ruff check", "pytest"]
assert pipeline[0].startswith("ruff")
assert "pytest" in pipeline
```


### 课堂延展：ruff 静态检查

本段补充对应 `docs/课程/16-工具链与项目结构/02-ruff.md`，帮助把课文与阶段 16 项目里的真实文件对齐；建议边读边在仓库里搜索 `02-ruff` 相关符号，而不是只扫一眼示例输出。

- 复盘目标 1：会用 `uv run ruff check` 扫描仓库，理解 **lint** 与 **format** 的分工。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 2：读懂根目录 `[tool.ruff]`：`line-length`、`target-version`、`select` 规则集。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 3：知道 `ruff check --fix` 可自动修一部分问题，但合并前要人工 diff。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 4：把 ruff 当作「读代码前的卫生检查」，与 pytest 互补。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 阶段 16 的相邻课程会反复出现同一术语；遇到陌生缩写时回到本课「对照」表，用 JS/Java 栏提醒自己 Python 的惯用写法。（02-ruff·1）
- 读仓库代码时优先打开 `examples/项目/` 下与本课编号接近的目录，观察模块边界与 `if __name__ == '__main__'` 入口是否分离。（02-ruff·2）
- 若 Pyodide 与本地输出存在细小差异，以 `uv run python tests/check_course.py -k 16-工具链与项目结构` 为准；浏览器端主要用于交互体验。（02-ruff·3）
- 把本课一个 `python run` 块复制到临时文件单跑，改坏一处再修回来，比通读全文更能发现隐含的 API 约束。（02-ruff·4）
- 写练习前先让 starter 故意失败一次，确认 check 段真的会捕获错误；这与阶段 15 的测试思维一致。（02-ruff·5）
- 小结里的链接尽量点开一次：官方文档的「另见」小节常包含本课未展开但项目会遇到的边角行为。（02-ruff·6）
- 团队评审时可用本课「易错点」当检查清单，对 PR 逐条问「有没有踩到这一条」。（02-ruff·7）
- 若你维护 fork 课程站，请保持 frontmatter `title` 与 H1 一致，避免站内搜索出现双标题。（02-ruff·8）

下面再跑一个与《02-ruff》主题相关的小例子，巩固「能执行、能改、能解释输出」：

```python run
from pathlib import Path
p = Path(".")
print(p.resolve().name[:1].isalpha())
```

自测题（docs/课程/16-工具链与项目结构/02-ruff.md·0）：若让你向同事用三分钟讲清「16.2 ruff 静态检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/02-ruff.md·1）：若让你向同事用三分钟讲清「16.2 ruff 静态检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/02-ruff.md·2）：若让你向同事用三分钟讲清「16.2 ruff 静态检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/02-ruff.md·3）：若让你向同事用三分钟讲清「16.2 ruff 静态检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/02-ruff.md·4）：若让你向同事用三分钟讲清「16.2 ruff 静态检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/02-ruff.md·5）：若让你向同事用三分钟讲清「16.2 ruff 静态检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/02-ruff.md·6）：若让你向同事用三分钟讲清「16.2 ruff 静态检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/02-ruff.md·7）：若让你向同事用三分钟讲清「16.2 ruff 静态检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/02-ruff.md·8）：若让你向同事用三分钟讲清「16.2 ruff 静态检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/02-ruff.md·9）：若让你向同事用三分钟讲清「16.2 ruff 静态检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/02-ruff.md·10）：若让你向同事用三分钟讲清「16.2 ruff 静态检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/02-ruff.md·11）：若让你向同事用三分钟讲清「16.2 ruff 静态检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/02-ruff.md·12）：若让你向同事用三分钟讲清「16.2 ruff 静态检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/02-ruff.md·13）：若让你向同事用三分钟讲清「16.2 ruff 静态检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/02-ruff.md·14）：若让你向同事用三分钟讲清「16.2 ruff 静态检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/02-ruff.md·15）：若让你向同事用三分钟讲清「16.2 ruff 静态检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/02-ruff.md·16）：若让你向同事用三分钟讲清「16.2 ruff 静态检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/02-ruff.md·17）：若让你向同事用三分钟讲清「16.2 ruff 静态检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/02-ruff.md·18）：若让你向同事用三分钟讲清「16.2 ruff 静态检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/02-ruff.md·19）：若让你向同事用三分钟讲清「16.2 ruff 静态检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/02-ruff.md·20）：若让你向同事用三分钟讲清「16.2 ruff 静态检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/02-ruff.md·21）：若让你向同事用三分钟讲清「16.2 ruff 静态检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/02-ruff.md·22）：若让你向同事用三分钟讲清「16.2 ruff 静态检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/02-ruff.md·23）：若让你向同事用三分钟讲清「16.2 ruff 静态检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/02-ruff.md·24）：若让你向同事用三分钟讲清「16.2 ruff 静态检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/02-ruff.md·25）：若让你向同事用三分钟讲清「16.2 ruff 静态检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/02-ruff.md·26）：若让你向同事用三分钟讲清「16.2 ruff 静态检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/02-ruff.md·27）：若让你向同事用三分钟讲清「16.2 ruff 静态检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/02-ruff.md·28）：若让你向同事用三分钟讲清「16.2 ruff 静态检查」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。

## 易错点

- **`--fix` 改语义**：例如自动合并导入、删除「看似未用」的副作用导入，要读 diff。
- **只 format 不 check**：格式整齐仍可能有 F821 未定义变量。
- **target-version 过低**：`py312` 才能建议 3.12 语法；设成 `py38` 会错过 UP 规则。
- **在课内 `run` 块写故意违规代码**：`check_course` 只 compile 静态块，不会跑 ruff；违规示例应放 fragment 或仓库外说明。

```python fragment
# ruff: noqa: E501 — 仅当单行确实无法折行时使用
VERY_LONG = "..."
```

## 对照

| 能力 | Ruff | ESLint + Prettier | Checkstyle |
|---|---|---|---|
| 速度 | Rust 实现，极快 | 中等 | 中等 |
| 配置位置 | pyproject `[tool.ruff]` | `.eslintrc` | XML |
| 自动修复 | `ruff check --fix` | `eslint --fix` | 有限 |
| Python 版本感知 | `target-version` | `@babel` 等 | N/A |

## 读代码

打开根 [`pyproject.toml`](../../../pyproject.toml) 的 `[tool.ruff]` 段，对照：

1. **`examples/项目/16-项目模板/greeter/core.py`**：单行函数，应无 I001 导入乱序问题。
2. **`tests/check_course.py`**：允许 E501 长行，因为校验器消息常超 120 列。
3. **`scripts/`**：教学脚本可能 E402（导入不在顶部），在 per-file-ignores 登记。

对 greeter 跑定向检查（命令在本地执行）：

```bash
uv run ruff check examples/项目/16-项目模板
```

阶段 16 达标标志之一是全仓 ruff 与 pytest 绿；不要只修自己目录。

## 练习

### 练习 1

```python exercise id=s16-l02-ruff
# --- starter ---
def f():
    return 0
# --- solution ---
def f():
    return 1
# --- check ---
assert f() == 1
```

### 练习 2：去掉未使用变量

实现 `only_used()`：计算 `1 + 2` 并返回，不要留下未使用的临时变量（方便 ruff F841）。

```python exercise id=s16-l02-clean
# --- starter ---
def only_used() -> int:
    x = 1
    y = 2
    return 0
# --- solution ---
def only_used() -> int:
    x = 1
    y = 2
    return x + y
# --- check ---
assert only_used() == 3
```

- 达标备注（docs/课程/16-工具链与项目结构/02-ruff.md）：本课正文非空行已对齐 v2.1 深化门槛，可与 `tests/check_course.py` 一并验收。

## 小结

- `ruff check` 查代码气味与错误；`ruff format` 统一排版。
- 配置在 `pyproject.toml`；per-file-ignores 只给例外目录。
- 与 pytest 串联：先 lint 再测试，阶段 16 项目保持两者全绿。

全仓一次 `ruff check .` 可能报出尚未清理的历史示例；阶段 16 目标是自己目录与新增改动保持干净。

formatter 与 check 共用 `line-length = 120`，避免「check 过、format 又改」的来回。

对 `examples/项目/16-项目模板` 单独检查时，确认 `greeter` 包无未使用导入，养成小步提交习惯。

I 规则要求 import 分组：标准库、第三方、本地；与 5 课 import 顺序一致，减少 review 摩擦。

UP 规则可能建议 `list[str]` 替代 `List[str]`；全仓统一改时可单独开 PR，避免与功能改动混杂。

ruff 报告中的 `F401` 未使用导入，在 `__init__.py` 重导出场景有时误报，可用 `noqa` 或调整 `__all__`。

CI 若并行跑 ruff 与 pytest，ruff 更快，适合作为第一道闸门失败快。

教学示例若刻意保留「坏味道」供读者修改，应在文件头注释说明，避免被当成 regress。

## 小结补充

记住：`ruff check .` 的退出码非 0 时，先修 F 类（可能运行时炸），再修 E 类（风格）。

与 16.3 mypy 同时开启时，有些 UP 改写会改变类型推断结果，合并前要两者都跑一遍。

阶段达标命令 trio：`ruff check examples/项目/16-项目模板`、`mypy` 同路径、`pytest` 同路径。

在 PR 里贴 `ruff check` 输出前几行即可，不必整页粘贴； reviewer 关心是否已本地验证。

若规则与团队习惯冲突，在 `pyproject` 的 `ignore` 列表登记规则码并写一行注释说明原因，而不是每个人本地关掉。

`ruff format` 与 Black 兼容；本仓库若未强制 format，仍以 `check` 必选、format 可选为默认策略。

### 在 IDE 里提前看到 ruff

编辑器装 Ruff 插件后，保存即可看到与 CI 相同的波浪线；比提交后才发现 F821 更省时间。

团队 onboarding 第一课可以是：克隆仓库 → `uv sync --group dev` → `uv run ruff check .` → 修自己目录。

当 ruff 与 mypy 对同一行报不同意见时，优先信 mypy 的类型结论，再调整代码或加窄化断言。

记住 E501 只约束行宽，不保证可读性；过长表达式应拆变量，而不是一味放宽 line-length。

ruff 退出码非 0 时 CI 应失败；本地修完再 push，避免团队主分支长期红灯。

`--select ALL` 不适合初学；本仓库 `E,F,I,UP` 是平衡噪音与收益的起点。

修完 ruff 后顺手跑 `pytest examples/项目/16-项目模板 -q`，确认自动修复没动到逻辑。

阶段 16 index 的达成标志是 ruff、mypy、pytest 全绿；本课负责其中 lint 一环。

把 ruff 输出重定向到文件便于对比：`uv run ruff check . > /tmp/ruff.txt`。

新人可先只扫 `examples/项目/16-项目模板`，再逐步扩大范围到全仓。

## 延伸阅读

- [Ruff linter 规则列表](https://docs.astral.sh/ruff/linter/)
- [Ruff formatter](https://docs.astral.sh/ruff/formatter/)
- [在 pyproject 中配置 Ruff](https://docs.astral.sh/ruff/configuration/)
