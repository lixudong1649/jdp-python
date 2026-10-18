---
title: 16.1 src 布局与 pyproject
---

# 16.1 src 布局与 pyproject

> 前置：5.2 包与项目结构 · 约 40 分钟 · 官方对应：[pyproject.toml 规范](https://packaging.python.org/en/latest/specifications/pyproject-toml/)、[uv 项目指南](https://docs.astral.sh/uv/guides/projects/) · 核对日期 2026-10-18（课程仓库 Python 3.12+）

## 目标

- 读懂根目录 `pyproject.toml` 的 `[project]`、`requires-python` 与 `[dependency-groups]`。
- 理解 **src 布局**（包在子目录里）与「平铺脚本」的差异，以及为何测试时要靠 `conftest` 注入路径。
- 知道 `uv.lock` 与 `pyproject` 应同步提交，保证团队装到同一组依赖。
- 对照阶段 16 项目 [`greeter`](../../../examples/项目/16-项目模板/greeter/core.py) 的小包结构。

## 核心概念

### pyproject 是单一清单

PEP 621 把项目元数据收敛到 `pyproject.toml`。本仓库片段：

```toml
[project]
name = "jdp-python"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "anthropic>=1.11.0",
    "python-dotenv>=1.2.4",
]
```

课内用 Python 读取 TOML 字符串示意（不依赖第三方解析器）：

```python run
snippet = """
[project]
name = "demo"
version = "0.1.0"
requires-python = ">=3.12"
"""
assert 'name = "demo"' in snippet
assert ">=3.12" in snippet
print("toml fragment ok")
```

### dependency-groups：可选能力分组

本仓库用 uv 的 `[dependency-groups]` 把 dev / data / web 分开，避免人人都装 pandas：

```toml
[dependency-groups]
dev = ["pytest>=9.1.1", "ruff>=0.17.1", "mypy>=2.4.0"]
```

安装 dev 工具：

```bash
uv sync --group dev
```

课内演示「组名 → 包列表」映射：

```python run
groups = {
    "dev": ["pytest", "ruff", "mypy"],
    "data": ["numpy", "pandas"],
}
assert "pytest" in groups["dev"]
assert "fastapi" not in groups.get("web", [])
print(groups["dev"])
```

### src 布局 vs 平铺

| 布局 | 目录示例 | 优点 |
|---|---|---|
| 平铺 | `examples/项目/14-日志统计CLI/logstats.py` | 学习 CLI 时路径直观 |
| 包目录 | `16-项目模板/greeter/core.py` | 导入边界清晰，适合打包 |
| src 布局 | `src/mypkg/__init__.py` | 测试强制从安装路径 import，防误导入仓库根 |

阶段 16 的 `greeter` 是**包目录**模板：`import greeter` 依赖 `examples/项目/conftest.py` 把各阶段目录插入 `sys.path`，与真实发布项目的 `pip install -e .` 不同——17 课会接到 wheel。

### pytest 与 pyproject 联动

```toml
[tool.pytest.ini_options]
testpaths = ["examples/项目", "tests"]
python_files = ["test_*.py"]
```

一条配置让根目录 `uv run pytest` 收集所有阶段测试与 `tests/check_course.py` 驱动的文档检查。

```python run
config = {"testpaths": ["examples/项目", "tests"], "python_files": ["test_*.py"]}
assert any("examples" in p for p in config["testpaths"])
assert config["python_files"][0].startswith("test_")
```


## 易错点

- **改 pyproject 不跑 `uv lock`**：锁文件过期会导致 CI 与同事环境不一致。
- **requires-python 写太宽**：课程统一 3.12+，用 3.10 语法却标 `>=3.8` 会在旧环境静默失败。
- **把业务依赖写进 dev 组**：运行时需要的包必须在 `[project] dependencies`。
- **在仓库根随意 `pip install`**：本课用 `uv run` / `uv sync`，避免污染全局 Python。

```python run raises=ValueError
def parse_version(s: str) -> tuple[int, ...]:
    return tuple(int(x) for x in s.split("."))

assert parse_version("3.12.1")[:2] == (3, 12)
parse_version("3.12.x")  # 非数字段会 ValueError
```

版本比较应使用 `packaging.version`，此处仅演示解析失败情形。

## 对照

| 概念 | Python (uv/pyproject) | Node.js | Java |
|---|---|---|---|
| 项目清单 | `pyproject.toml` | `package.json` | `pom.xml` / Gradle |
| 锁文件 | `uv.lock` | `package-lock.json` | Gradle lock |
| 可选组 | `dependency-groups` | `optionalDependencies` | BOM / profile |
| 解释器约束 | `requires-python` | `engines` | `--release` |

## 读代码

阶段 16 项目结构：

```
examples/项目/16-项目模板/
  greeter/
    __init__.py      # 导出 greet
    core.py          # 实现
  test_greeter.py    # pytest
```

**`greeter/core.py`**

```python
def greet(name: str) -> str:
    return f"hello, {name}"
```

**`greeter/__init__.py`**

```python
from greeter.core import greet

__all__ = ["greet"]
```

- 对外只暴露 `greet`，内部模块名 `core` 可重构。
- `test_greeter.py` 写 `from greeter import greet`，与用户使用方式一致。

根目录 [`pyproject.toml`](../../../pyproject.toml) 的 `[tool.ruff]`、`[tool.pytest.ini_options]` 是「全仓工具链」配置；小项目可复制片段到自己的 pyproject。

验证：

```bash
uv run pytest examples/项目/16-项目模板 -q
```

## 练习

### 练习 1

```python exercise id=s16-l01-toml
# --- starter ---
name = 'demo'
# --- solution ---
name = 'demo'
version = '0.0.1'
# --- check ---
assert version == '0.0.1'
```

### 练习 2：解析简易版本元组

实现 `project_tuple(name: str, version: str) -> tuple[str, str]`，返回 `(name, version)`，供测试断言。

```python exercise id=s16-l01-meta
# --- starter ---
def project_tuple(name: str, version: str) -> tuple[str, str]:
    return ("", "")
# --- solution ---
def project_tuple(name: str, version: str) -> tuple[str, str]:
    return (name, version)
# --- check ---
assert project_tuple("demo", "0.1.0") == ("demo", "0.1.0")
```


## 小结

- `pyproject.toml` 声明项目名、Python 版本、依赖与工具配置；`uv.lock` 锁定解析结果。
- 阶段 16 `greeter` 展示包目录 + `__init__` 重导出；路径由 `conftest` 或安装注入。
- 全仓 `pytest` / `ruff` 配置集中在根 pyproject，阶段项目共享同一工具链。

阶段 17 会把 `logstats_pkg` 接到 wheel；届时回头看本课 dependency-groups 与 pytest 配置是否仍适用。

`uv run` 无需手动激活虚拟环境，适合教程与 CI 同一入口。

阅读锁文件时，关注 `requires-python` 与解析出的 wheel 标签是否匹配本机 3.12。

## 延伸阅读

- [pyproject.toml 规范](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
- [uv 项目结构](https://docs.astral.sh/uv/guides/projects/)
- [pytest 配置](https://docs.pytest.org/en/stable/reference/customize.html)
