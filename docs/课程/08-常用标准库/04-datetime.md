---
title: 8.4 datetime
---

# 8.4 datetime

> 前置：7.1 · 约 25 分钟 · 官方对应：[datetime](https://docs.python.org/zh-cn/3/library/datetime.html)、[zoneinfo](https://docs.python.org/zh-cn/3/library/zoneinfo.html) · 核对日期 2026-10-06

## 目标

- 区分 naive（无时区）与 aware（带时区）时间，默认使用 aware 时间。
- 掌握格式化（`strftime`、`isoformat`）与解析（`strptime`、`fromisoformat`）。
- 用 `timedelta` 做时间运算；知道时间戳与 `datetime` 的转换。

## 核心概念

### 主要类型

| 类型 | 表示 | 例子 |
|---|---|---|
| `date` | 日期 | `date(2026, 10, 6)` |
| `time` | 一天中的时刻 | `time(22, 30)` |
| `datetime` | 日期 + 时刻（可带时区） | `datetime(2026, 10, 6, 22, 30, tzinfo=UTC)` |
| `timedelta` | 时间间隔 | `timedelta(days=1, hours=2)` |
| `timezone` / `ZoneInfo` | 时区 | `timezone.utc`、`ZoneInfo("Asia/Shanghai")` |

### naive 与 aware

没有 `tzinfo` 的 `datetime` 是 **naive** 的：它不知道自己是哪个时区的时间，跨时区比较和计算时容易出错。**存储和传输一律用 aware 的 UTC 时间，展示时再转为本地时区。**

```python run
from datetime import datetime, timedelta, timezone

now_utc = datetime.now(timezone.utc)                 # aware：推荐
naive = datetime(2026, 10, 6, 22, 0)                 # naive
print(now_utc.tzinfo, naive.tzinfo)

CST = timezone(timedelta(hours=8), "CST")            # 固定偏移时区
t = datetime(2026, 10, 6, 22, 0, tzinfo=CST)
print(t.isoformat())                                 # 2026-10-06T22:00:00+08:00
print(t.astimezone(timezone.utc).isoformat())        # 转为 UTC：14:00
```

真实代码中更常用 IANA 时区名（会自动处理夏令时）：

```python
from datetime import datetime
from zoneinfo import ZoneInfo

now_sh = datetime.now(ZoneInfo("Asia/Shanghai"))
now_ny = now_sh.astimezone(ZoneInfo("America/New_York"))
```

`zoneinfo` 依赖系统时区数据库；Windows 或精简环境中需安装 `tzdata` 包。

### 格式化与解析

```python run
from datetime import datetime, timezone

t = datetime(2026, 10, 6, 9, 5, 3, tzinfo=timezone.utc)
print(t.isoformat())                         # ISO 8601：API 与日志首选
print(t.strftime("%Y-%m-%d %H:%M:%S %Z"))    # 自定义格式
print(f"{t:%Y年%m月%d日}")                    # f-string 中直接写格式

parsed = datetime.fromisoformat("2026-10-06T09:05:03+00:00")
print(parsed == t)
p2 = datetime.strptime("2026/10/06 09:05", "%Y/%m/%d %H:%M")   # 得到 naive
print(p2, p2.tzinfo)
print(p2.replace(tzinfo=timezone.utc).isoformat())            # 补上时区（确认它本来就是 UTC 时）
```

| 指令 | 含义 | 指令 | 含义 |
|---|---|---|---|
| `%Y` | 4 位年 | `%H` | 24 小时制小时 |
| `%m` | 月（01–12） | `%M` | 分钟 |
| `%d` | 日 | `%S` | 秒 |
| `%z` | `+0800` 形式的偏移 | `%a` / `%A` | 星期缩写/全称 |

### 运算与时间戳

```python run
from datetime import datetime, timedelta, timezone

start = datetime(2026, 10, 6, 8, 0, tzinfo=timezone.utc)
end = start + timedelta(hours=2, minutes=30)
print(end, end - start, (end - start).total_seconds())
print(end > start)

ts = start.timestamp()                                   # 时间戳：自 1970-01-01 UTC 起的秒数
print(ts, datetime.fromtimestamp(ts, tz=timezone.utc))
```

## 易错点

- **naive 与 aware 不能比较大小或相减**：抛 `TypeError: can't compare offset-naive and offset-aware datetimes`；而 `==` 不报错，直接返回 `False`。
- **`datetime.utcnow()` 返回 naive 时间**，3.12 起已弃用；用 `datetime.now(timezone.utc)`（3.11 起也可 `from datetime import UTC` 后写 `datetime.now(UTC)`）。
- **`fromtimestamp(ts)` 不传 `tz`** 得到本地时区的 naive 时间，结果因机器而异。
- **`strptime` 解析结果是 naive 的**，即使字符串里看起来是 UTC。

```python run raises=TypeError
from datetime import datetime, timezone

aware = datetime.now(timezone.utc)
naive = datetime(2026, 10, 6)
print(aware > naive)
```

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 当前 UTC 时间 | `datetime.now(timezone.utc)` | `new Date()`（内部为 UTC） | `Instant.now()` |
| 带时区时间 | aware `datetime` | `Temporal.ZonedDateTime` | `ZonedDateTime` |
| 无时区时间 | naive `datetime` | `Temporal.PlainDateTime` | `LocalDateTime` |
| 间隔 | `timedelta` | `Temporal.Duration` | `Duration` |
| ISO 格式化 | `t.isoformat()` | `d.toISOString()` | `t.toString()` |

## 读代码

API 响应中的时间通常是 ISO 8601 字符串（如 `"2026-10-06T14:00:00Z"`），代码这样处理：

```python
from datetime import datetime, timezone

created = datetime.fromisoformat(item["created_at"])   # 3.11 起支持末尾的 "Z"
age = datetime.now(timezone.utc) - created
if age.total_seconds() > 3600:
    ...
```

`minimal_agent.py` 本身不处理时间；11.2 的改造练习中，你会给它增加一个 `get_time` 工具（练习中返回固定值，便于断言）。

## 练习

### 练习 1：时区转换

实现 `to_utc_iso(text)`：输入形如 `"2026-10-06 22:00"` 的北京时间（UTC+8）字符串，返回 UTC 时间的 ISO 字符串，例如 `"2026-10-06T14:00:00+00:00"`。

```python exercise id=s08-l04-utc
# --- starter ---
from datetime import datetime, timedelta, timezone

def to_utc_iso(text):
    return datetime.strptime(text, "%Y-%m-%d %H:%M").isoformat()
# --- solution ---
from datetime import datetime, timedelta, timezone

CST = timezone(timedelta(hours=8))

def to_utc_iso(text):
    local = datetime.strptime(text, "%Y-%m-%d %H:%M").replace(tzinfo=CST)
    return local.astimezone(timezone.utc).isoformat()
# --- check ---
assert to_utc_iso("2026-10-06 22:00") == "2026-10-06T14:00:00+00:00", to_utc_iso("2026-10-06 22:00")
assert to_utc_iso("2026-10-07 03:30") == "2026-10-06T19:30:00+00:00"
```

### 练习 2：耗时描述

实现 `elapsed(start_iso, end_iso)`：两个带时区的 ISO 字符串，返回间隔的整数分钟数。

```python exercise id=s08-l04-elapsed
# --- starter ---
from datetime import datetime

def elapsed(start_iso, end_iso):
    return 0
# --- solution ---
from datetime import datetime

def elapsed(start_iso, end_iso):
    delta = datetime.fromisoformat(end_iso) - datetime.fromisoformat(start_iso)
    return int(delta.total_seconds() // 60)
# --- check ---
assert elapsed("2026-10-06T08:00:00+00:00", "2026-10-06T10:30:00+00:00") == 150
assert elapsed("2026-10-06T22:00:00+08:00", "2026-10-06T14:10:00+00:00") == 10, "不同时区也应正确计算"
```

## 小结

- 默认用 aware 时间：`datetime.now(timezone.utc)`；展示时 `astimezone` 转换。
- ISO 8601：`isoformat()` 输出，`fromisoformat()` 解析。
- `timedelta` 做加减；`total_seconds()` 取秒数。
- naive 与 aware 混用会报 `TypeError`。

## 延伸阅读

- [datetime](https://docs.python.org/zh-cn/3/library/datetime.html)
- [感知型与简单型对象](https://docs.python.org/zh-cn/3/library/datetime.html#aware-and-naive-objects)
- [strftime() 和 strptime() 格式码](https://docs.python.org/zh-cn/3/library/datetime.html#format-codes)
- [zoneinfo](https://docs.python.org/zh-cn/3/library/zoneinfo.html)
