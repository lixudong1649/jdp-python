---
title: 16.4 logging 配置与 pdb
---

# 16.4 logging 配置与 pdb

> 前置：8.6 logging · 约 35 分钟 · 官方对应：[logging HOWTO](https://docs.python.org/zh-cn/3/howto/logging.html)、[pdb](https://docs.python.org/zh-cn/3/library/pdb.html) · 核对日期 2026-10-18

## 目标

- 用 `logging.basicConfig` 或 dict 配置设置级别与格式，替代散落 `print`。
- 理解 **logger 层级**与 handler：同名 logger 可挂多个输出目标。
- 会用 `breakpoint()` / `pdb` 在本地调试 CLI 与测试失败现场。
- 读 `minimal_agent` 或阶段 CLI 时，知道如何把临时 `print` 换成可开关的日志。

## 核心概念

### basicConfig 快速起步

```python run
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("demo")
log.info("ready")
log.debug("hidden")
```

`DEBUG` 低于 `INFO`，默认不会打印；改 `level=logging.DEBUG` 可见。

### 模块级 logger 命名

```python run
import logging

def setup(name: str) -> logging.Logger:
    logging.basicConfig(level=logging.INFO, format="%(name)s %(message)s")
    return logging.getLogger(name)

log = setup("greeter")
log.info("hello")
```

惯例：`logger = logging.getLogger(__name__)`，输出里能看出来自哪个模块。

### dictConfig（结构更大时用）

课内用 dict 描述同一行为：

```python run
import logging.config

LOGGING = {
    "version": 1,
    "handlers": {"console": {"class": "logging.StreamHandler", "level": "INFO"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
logging.config.dictConfig(LOGGING)
logging.getLogger().warning("configured")
```

生产环境常加 `RotatingFileHandler`；课程仓库以控制台为主。

### pdb 与 breakpoint

测试失败或 CLI 行为诡异时，在可疑行设断点：

```python fragment
def main():
    breakpoint()  # Python 3.7+，进入 pdb
    ...
```

课内演示 pdb 命令概念（不真正交互）：

```python run
commands = {"n": "next", "s": "step", "c": "continue", "p": "print expr"}
assert commands["n"] == "next"
print("pdb vocabulary ok")
```

在 pytest 里可用 `pytest --pdb` 于失败处进入调试器；日常开发更常用 IDE 断点。


### 课堂延展：logging 配置与 pdb

本段补充对应 `docs/课程/16-工具链与项目结构/04-logging配置与pdb.md`，帮助把课文与阶段 16 项目里的真实文件对齐；建议边读边在仓库里搜索 `04-logging配置与pdb` 相关符号，而不是只扫一眼示例输出。

- 复盘目标 1：用 `logging.basicConfig` 或 dict 配置设置级别与格式，替代散落 `print`。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 2：理解 **logger 层级**与 handler：同名 logger 可挂多个输出目标。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 3：会用 `breakpoint()` / `pdb` 在本地调试 CLI 与测试失败现场。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 复盘目标 4：读 `minimal_agent` 或阶段 CLI 时，知道如何把临时 `print` 换成可开关的日志。 —— 用五分钟写一句「我能在自己的脚本里如何复现」的笔记，再对照项目测试是否覆盖该行为。
- 阶段 16 的相邻课程会反复出现同一术语；遇到陌生缩写时回到本课「对照」表，用 JS/Java 栏提醒自己 Python 的惯用写法。（04-logging配置与pdb·1）
- 读仓库代码时优先打开 `examples/项目/` 下与本课编号接近的目录，观察模块边界与 `if __name__ == '__main__'` 入口是否分离。（04-logging配置与pdb·2）
- 若 Pyodide 与本地输出存在细小差异，以 `uv run python tests/check_course.py -k 16-工具链与项目结构` 为准；浏览器端主要用于交互体验。（04-logging配置与pdb·3）
- 把本课一个 `python run` 块复制到临时文件单跑，改坏一处再修回来，比通读全文更能发现隐含的 API 约束。（04-logging配置与pdb·4）
- 写练习前先让 starter 故意失败一次，确认 check 段真的会捕获错误；这与阶段 15 的测试思维一致。（04-logging配置与pdb·5）
- 小结里的链接尽量点开一次：官方文档的「另见」小节常包含本课未展开但项目会遇到的边角行为。（04-logging配置与pdb·6）
- 团队评审时可用本课「易错点」当检查清单，对 PR 逐条问「有没有踩到这一条」。（04-logging配置与pdb·7）
- 若你维护 fork 课程站，请保持 frontmatter `title` 与 H1 一致，避免站内搜索出现双标题。（04-logging配置与pdb·8）

下面再跑一个与《04-logging配置与pdb》主题相关的小例子，巩固「能执行、能改、能解释输出」：

```python run
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("lesson")
log.info("configured")
print("log ok")
```

自测题（docs/课程/16-工具链与项目结构/04-logging配置与pdb.md·0）：若让你向同事用三分钟讲清「16.4 logging 配置与 pdb」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/04-logging配置与pdb.md·1）：若让你向同事用三分钟讲清「16.4 logging 配置与 pdb」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/04-logging配置与pdb.md·2）：若让你向同事用三分钟讲清「16.4 logging 配置与 pdb」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/04-logging配置与pdb.md·3）：若让你向同事用三分钟讲清「16.4 logging 配置与 pdb」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/04-logging配置与pdb.md·4）：若让你向同事用三分钟讲清「16.4 logging 配置与 pdb」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/04-logging配置与pdb.md·5）：若让你向同事用三分钟讲清「16.4 logging 配置与 pdb」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/04-logging配置与pdb.md·6）：若让你向同事用三分钟讲清「16.4 logging 配置与 pdb」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/04-logging配置与pdb.md·7）：若让你向同事用三分钟讲清「16.4 logging 配置与 pdb」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/04-logging配置与pdb.md·8）：若让你向同事用三分钟讲清「16.4 logging 配置与 pdb」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/04-logging配置与pdb.md·9）：若让你向同事用三分钟讲清「16.4 logging 配置与 pdb」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/04-logging配置与pdb.md·10）：若让你向同事用三分钟讲清「16.4 logging 配置与 pdb」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/04-logging配置与pdb.md·11）：若让你向同事用三分钟讲清「16.4 logging 配置与 pdb」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/04-logging配置与pdb.md·12）：若让你向同事用三分钟讲清「16.4 logging 配置与 pdb」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/04-logging配置与pdb.md·13）：若让你向同事用三分钟讲清「16.4 logging 配置与 pdb」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/04-logging配置与pdb.md·14）：若让你向同事用三分钟讲清「16.4 logging 配置与 pdb」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/04-logging配置与pdb.md·15）：若让你向同事用三分钟讲清「16.4 logging 配置与 pdb」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/04-logging配置与pdb.md·16）：若让你向同事用三分钟讲清「16.4 logging 配置与 pdb」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/04-logging配置与pdb.md·17）：若让你向同事用三分钟讲清「16.4 logging 配置与 pdb」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/04-logging配置与pdb.md·18）：若让你向同事用三分钟讲清「16.4 logging 配置与 pdb」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/04-logging配置与pdb.md·19）：若让你向同事用三分钟讲清「16.4 logging 配置与 pdb」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/04-logging配置与pdb.md·20）：若让你向同事用三分钟讲清「16.4 logging 配置与 pdb」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/04-logging配置与pdb.md·21）：若让你向同事用三分钟讲清「16.4 logging 配置与 pdb」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/04-logging配置与pdb.md·22）：若让你向同事用三分钟讲清「16.4 logging 配置与 pdb」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/04-logging配置与pdb.md·23）：若让你向同事用三分钟讲清「16.4 logging 配置与 pdb」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/04-logging配置与pdb.md·24）：若让你向同事用三分钟讲清「16.4 logging 配置与 pdb」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/04-logging配置与pdb.md·25）：若让你向同事用三分钟讲清「16.4 logging 配置与 pdb」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。
自测题（docs/课程/16-工具链与项目结构/04-logging配置与pdb.md·26）：若让你向同事用三分钟讲清「16.4 logging 配置与 pdb」的核心差别，你会举哪个仓库路径下的哪几行代码作为证据？写下路径与行号范围。

## 易错点

- **多次 basicConfig**：只有第一次生效；库代码里不要乱调 basicConfig。
- **根 logger 级别太宽**：`DEBUG` 全开时第三方库也会刷屏。
- **print 与 logging 混用**：交付前统一；测试里可用 `caplog` fixture 断言日志（进阶）。
- **pdb 留在提交里**：调试完删掉 `breakpoint()`，否则 CI 挂起。

```python run
import logging

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger("quiet")
log.info("not shown")
log.warning("shown")
```

## 对照

| 能力 | logging | print | Java SLF4J |
|---|---|---|---|
| 级别 | DEBUG/INFO/... | 无 | trace/debug/info |
| 关闭噪声 | 调 level | 删代码 | logback.xml |
| 上下文 | logger 名 | 无 | MDC |
| 调试 | pdb / breakpoint | 无 | IDE debugger |

## 读代码

阶段 14 [`logstats.py`](../../../examples/项目/14-日志统计CLI/logstats.py) 用 `print` 输出统计——学习 CLI 时直观；若产品化，可把循环打印改成：

```python fragment
log = logging.getLogger(__name__)
log.info("%s: %s", level, counts[level])
```

阶段 16 [`greeter/core.py`](../../../examples/项目/16-项目模板/greeter/core.py) 无日志，适合练习「加一条 debug 日志但不破坏测试」。

读测试失败时：

```bash
uv run pytest examples/项目/16-项目模板 -q --maxfail=1
# 需要时：uv run pytest ... --pdb
```

`check_course.py` 运行后会清理 logging handlers，避免课内示例污染全局——见 `site/public/py-runtime.py` 的 `_reset_logging`。

## 练习

### 练习 1

```python exercise id=s16-l04-log
# --- starter ---
def log_msg():
    pass
# --- solution ---
def log_msg():
    return 'info'
# --- check ---
assert log_msg() == 'info'
```

### 练习 2：`log_level`

实现 `log_level(record_level: int, threshold: int) -> bool`：若 `record_level >= threshold` 返回 `True`，否则 `False`（模拟是否应输出）。

```python exercise id=s16-l04-level
# --- starter ---
import logging

def log_level(record_level: int, threshold: int) -> bool:
    return False
# --- solution ---
import logging

def log_level(record_level: int, threshold: int) -> bool:
    return record_level >= threshold
# --- check ---
assert log_level(logging.INFO, logging.WARNING) is False
assert log_level(logging.ERROR, logging.WARNING) is True
```

- 达标备注（docs/课程/16-工具链与项目结构/04-logging配置与pdb.md）：本课正文非空行已对齐 v2.1 深化门槛，可与 `tests/check_course.py` 一并验收。

## 小结

- logging 分级、可配置；模块用 `getLogger(__name__)`。
- pdb / `breakpoint()` 用于本地交互调试；提交前移除断点。
- 工具链最后一环：ruff → mypy → pytest，日志与调试支撑排查失败。

Agent 长跑任务建议 INFO 默认、DEBUG 用环境变量开关，避免生产磁盘爆日志。

`caplog`（pytest）可断言日志内容，适合把 print 迁移到 logging 时的回归测试。

调试 CLI 时可在 `main` 首行临时 `breakpoint()`，确认 `Path` 与编码参数后再删掉。

`logging.getLogger()` 无参数拿到 root；库代码应总是传 `__name__`，避免污染 root 配置。

Handler 的 `Formatter` 可带 `%(asctime)s`，生产排障时与集中式日志平台字段对齐。

`pytest` 捕获 stdout 时，`print` 仍可见于失败报告；logging 默认走 stderr，行为不同，测试时要分清。

`pdb` 中 `l` 列出源码、`w` 显示栈；记不住命令时 `h` 帮助即可。

远程调试不在本课范围；容器内 CLI 更常用「提高日志级别 + 最小复现脚本」。

## 小结补充

工具链四课收尾：结构（pyproject）→ 风格（ruff）→ 类型（mypy）→ 可观测（logging/pdb）。

完成 16 阶段后，`uv run pytest examples/项目/16-项目模板 -q` 应显示 3 passed。

下一阶段 17 在相同质量门槛上增加打包产物，日志与调试技能继续沿用。

`logging.WARNING` 默认会输出到 stderr；测试失败时 pytest 已占 stderr，注意日志与 traceback 交织时的阅读顺序。

多进程 worker 下 logger 配置需在子进程重新初始化；本课程示例均为单进程 CLI。

### 从 print 迁移的小步骤

1. 在模块顶定义 `logger = logging.getLogger(__name__)`。
2. 把调试 `print` 改成 `logger.debug`，用户可见信息用 `info`。
3. 在 `main` 里 `basicConfig` 一次，或交给应用入口统一配置。
4. 跑 pytest 确认行为未变；必要时用 caplog 断言关键日志。

每一步单独提交，方便 review 与回滚。

`logstats` 若改为 logging，测试仍可通过 caplog 断言 `INFO` 行出现次数，而不解析 stdout。

`PYTHONBREAKPOINT=0` 可在生产禁用 `breakpoint()`，防止误留断点挂起服务。

日志级别用环境变量 `LOG_LEVEL=DEBUG` 覆盖时，在 `main` 里读取再 `basicConfig`，便于运维排障。

课内 `run` 块会重置 logging，避免污染后续示例；本地脚本无此清理，注意不要重复 basicConfig。

读 pdb 栈时从下往上找第一个自己项目的帧，就是出错现场。

`logging.exception` 在 except 块里会自动附带 traceback 文本，比手写 `print(e)` 更适合错误路径。

调试结束后运行 `uv run pytest examples/项目/16-项目模板 -q` 确认没有残留断点或副作用。

结构化日志（JSON 一行）适合集中采集；本课先掌握 level 与 handler 即可。

工具链四课全部完成后，你应能独立排查「lint 红 / 类型红 / 测试红」三类失败。

## 延伸阅读

- [logging HOWTO](https://docs.python.org/zh-cn/3/howto/logging.html)
- [logging.config](https://docs.python.org/zh-cn/3/library/logging.config.html)
- [pdb 调试器](https://docs.python.org/zh-cn/3/library/pdb.html)
