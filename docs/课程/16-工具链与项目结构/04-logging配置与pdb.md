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

课内用 `sys.settrace` 模拟 pdb 的逐行停顿（pdb 本身就建立在这个钩子上，这里不进入交互）：

```python run
import sys


def demo(x: int) -> int:
    y = x + 1
    z = y * 2
    return z


first = demo.__code__.co_firstlineno
steps = []


def tracer(frame, event, arg):
    if frame.f_code is demo.__code__:
        if event == "line":
            steps.append((frame.f_lineno - first, dict(frame.f_locals)))
        return tracer
    return None


sys.settrace(tracer)
result = demo(3)
sys.settrace(None)
for offset, local_vars in steps:
    print("n -> 函数第", offset, "行，执行前 locals", local_vars)
stop = next(v for _, v in steps if "y" in v)
print("停在 z = y * 2 时 p y ->", stop["y"])
print("demo(3) =", result)
```

每条 `n ->` 对应一次 `line` 事件，也就是 pdb 里按一次 `n` 停下的位置；打印的 locals 是**这一行执行之前**的局部变量，所以第 1 行只有 `x`，到第 2 行才看得到 `y`。最后一行相当于在 `z = y * 2` 处 `p y`，`s`（step into）则对应 `call` 事件进入被调函数。

在 pytest 里可用 `pytest --pdb` 于失败处进入调试器；日常开发更常用 IDE 断点。


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
