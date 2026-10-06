---
title: 8.6 logging
---

# 8.6 logging

> 前置：5.1 · 约 25 分钟 · 官方对应：[日志指南](https://docs.python.org/zh-cn/3/howto/logging.html)、[logging](https://docs.python.org/zh-cn/3/library/logging.html)

## 目标

- 理解 logger、handler、level、formatter 四个概念。
- 用 `logging.basicConfig` 配置程序日志，用 `logging.getLogger(__name__)` 获取模块 logger。
- 知道库代码为什么用 logging 而不用 `print`，以及如何打开第三方库的调试日志。

## 核心概念

### 级别

| 级别 | 数值 | 用途 |
|---|---|---|
| `DEBUG` | 10 | 详细调试信息 |
| `INFO` | 20 | 正常运行的关键事件 |
| `WARNING` | 30 | 意外但可继续（**默认阈值**） |
| `ERROR` | 40 | 某个操作失败 |
| `CRITICAL` | 50 | 程序可能无法继续 |

### 基本用法

```python run
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
)
log = logging.getLogger("agent")          # 模块中通常写 logging.getLogger(__name__)

log.debug("不会输出：低于 INFO")
log.info("第 %d 轮：调用工具 %s", 1, "get_weather")   # 用 %s 占位，参数单独传
log.warning("超过最大轮数 %d", 5)
try:
    {}["x"]
except KeyError:
    log.exception("工具执行失败")           # ERROR 级别，并自动附上 Traceback
```

`basicConfig` 只在根 logger 还没有 handler 时生效一次，应当在程序入口处调用；**库代码不应调用它**。

### 结构：logger → handler → formatter

- **logger**：按名字组成层级（`"anthropic"` 是 `"anthropic._base_client"` 的父级），日志会向上传播给父 logger。
- **handler**：决定输出到哪里（终端、文件、网络）。
- **formatter**：决定格式。
- **level**：logger 和 handler 都可设置阈值。

```python run
import logging
import sys

root = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("[%(name)s] %(levelname)s %(message)s"))
root.addHandler(handler)
root.setLevel(logging.WARNING)

logging.getLogger("myapp").warning("应用日志")
sdk_logger = logging.getLogger("fake_sdk.http")
sdk_logger.debug("默认看不到 SDK 的调试日志")
logging.getLogger("fake_sdk").setLevel(logging.DEBUG)   # 只放开某个库
handler.setLevel(logging.DEBUG)
sdk_logger.debug("现在能看到 fake_sdk 的调试日志")
```

### 为什么不用 print

| | `print` | `logging` |
|---|---|---|
| 关闭/过滤 | 只能删代码 | 调级别即可，按模块控制 |
| 输出目标 | stdout | 终端、文件、日志系统，可多个 |
| 上下文 | 手写 | 时间、级别、模块、行号、Traceback |
| 库代码 | 污染调用方输出 | 由应用决定是否显示 |

## 易错点

- **在日志中用 f-string**：`log.debug(f"…{big}")` 即使不输出也会先格式化；推荐 `log.debug("… %s", big)`，只有真正输出时才格式化。
- **`basicConfig` 不生效**：之前已经有 handler（例如某个库或之前的调用已配置）；3.8 起可传 `force=True`。
- **重复输出**：给子 logger 和根 logger 都加了 handler，消息传播后被输出两次；设置 `logger.propagate = False` 或只在根上加 handler。
- **记录密钥**：日志会长期保存，避免记录请求头或完整配置。

```python run
import logging
import sys

logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(name)s %(message)s")
child = logging.getLogger("dup")
child.addHandler(logging.StreamHandler(sys.stdout))
child.info("这条会出现两次：子 logger 的 handler 一次，传播到根 logger 再一次")
```

## 对照

| 概念 | Python logging | JS | Java |
|---|---|---|---|
| 获取 logger | `logging.getLogger(__name__)` | 第三方（pino、winston） | `LoggerFactory.getLogger(X.class)`（SLF4J） |
| 占位符 | `log.info("x=%s", x)` | 各库不同 | `log.info("x={}", x)` |
| 附带异常 | `log.exception(...)` | `logger.error({ err })` | `log.error("...", e)` |
| 配置 | `basicConfig` / `dictConfig` | 代码配置 | `logback.xml` |

## 读代码

`minimal_agent.py` 用 `print` 输出 `[配置]`、`[第 N 轮]` 等信息——作为演示脚本，直观即可。若把它改造成可复用模块，应改为：

```python
import logging

log = logging.getLogger(__name__)
...
log.info("第 %d 轮：调用工具 %s(%s) -> %s", turn, block.name, block.input, output)
```

调试 SDK 网络请求时，可以只放开 SDK 自己的 logger（logger 名与包名一致）：

```python
logging.basicConfig(level=logging.INFO)
logging.getLogger("anthropic").setLevel(logging.DEBUG)
```

许多 SDK 也支持用环境变量开启调试日志：anthropic 1.11.0 支持 `ANTHROPIC_LOG=debug` 或 `info`（核对日期 2026-10-06）。注意调试日志可能包含请求细节，不要长期保存或外传。

## 练习

### 练习 1：配置模块 logger

实现 `make_logger(name, stream)`：返回名为 `name` 的 logger，级别为 `INFO`；为它添加一个写入 `stream` 的 `StreamHandler`，格式为 `"%(levelname)s %(name)s: %(message)s"`；并设置 `propagate = False`（避免重复输出）。

```python exercise id=s08-l06-logger
# --- starter ---
import logging

def make_logger(name, stream):
    return logging.getLogger(name)
# --- solution ---
import logging

def make_logger(name, stream):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
    logger.addHandler(handler)
    logger.propagate = False
    return logger
# --- check ---
import io
buf = io.StringIO()
log = make_logger("agent.check", buf)
log.debug("hidden")
log.info("第 %d 轮", 2)
log.warning("注意")
assert buf.getvalue() == "INFO agent.check: 第 2 轮\nWARNING agent.check: 注意\n", repr(buf.getvalue())
assert log.propagate is False
```

### 练习 2：延迟格式化

`log_turn(log, turn, name)` 用 f-string 记录日志。改为占位符写法：消息模板为 `"第 %d 轮调用 %s"`，参数单独传入。检查会验证 `LogRecord` 的 `msg` 与 `args`。

```python exercise id=s08-l06-lazy
# --- starter ---
def log_turn(log, turn, name):
    log.info(f"第 {turn} 轮调用 {name}")
# --- solution ---
def log_turn(log, turn, name):
    log.info("第 %d 轮调用 %s", turn, name)
# --- check ---
import logging
records = []

class Collect(logging.Handler):
    def emit(self, record):
        records.append(record)

lg = logging.getLogger("lazy.check")
lg.setLevel(logging.INFO)
lg.addHandler(Collect())
lg.propagate = False
log_turn(lg, 3, "get_weather")
r = records[-1]
assert r.msg == "第 %d 轮调用 %s", f"msg 应为模板，实际为 {r.msg!r}"
assert r.args == (3, "get_weather")
assert r.getMessage() == "第 3 轮调用 get_weather"
```

## 小结

- 级别从低到高 DEBUG → CRITICAL，默认阈值 WARNING。
- 程序入口 `basicConfig` 一次；模块里 `logging.getLogger(__name__)`。
- 日志用 `%s` 占位延迟格式化；`log.exception` 自动附带 Traceback。
- 只放开某个库的日志：`logging.getLogger("库名").setLevel(logging.DEBUG)`。

## 延伸阅读

- [日志指南（基础与进阶）](https://docs.python.org/zh-cn/3/howto/logging.html)
- [日志操作手册](https://docs.python.org/zh-cn/3/howto/logging-cookbook.html)
- [logging 模块](https://docs.python.org/zh-cn/3/library/logging.html)
