---
title: 阶段 8 · 常用标准库
goal: 认识 pathlib / json / os / datetime / collections / logging 的典型用法与坑
---

# 阶段 8 · 常用标准库

**达成标志**：读代码遇到这些模块时，知道它们在做什么、有哪些常见坑。

| 课程 | 你将学会 |
|---|---|
| [8.1 pathlib 与文件](01-pathlib与文件.md) | 路径拼接、遍历、读写文件、编码 |
| [8.2 json](02-json.md) | `dumps`/`loads`/`dump`/`load`、中文与缩进、类型对应 |
| [8.3 os、sys 与环境变量](03-os-sys与环境变量.md) | `os.environ`/`os.getenv`、`.env` 机制、`sys.argv`、退出码 |
| [8.4 datetime](04-datetime.md) | 时区感知时间、格式化与解析、时间运算 |
| [8.5 collections 与 itertools](05-collections与itertools.md) | `Counter`、`defaultdict`、`deque`、`namedtuple`、`itertools` 常用函数 |
| [8.6 logging](06-logging.md) | logger / handler / level、`basicConfig`、为什么库代码不用 `print` |

**与终点的关系**：`os.getenv` 与 `load_dotenv()` 决定了 `minimal_agent.py` 连接哪个服务、用哪个密钥；工具参数 `block.input` 本质上是模型生成的 JSON。
