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
