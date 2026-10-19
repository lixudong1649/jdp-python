# jdp-python v2.3 Goal：把弱示例改写成真正讲清本课概念的示例

> 2026-10-19（北京时间）。按知识库《Goal 提示词编写与验收标准》编写（含新增第九节硬门槛，原样贴在本文第 7 节）。asahi 已批准本轮。模型：composer-2.5。
> 前序 goal（`Goal-v2.1-课程深化重写.md`、`Goal-v2.2-去凑数返工.md`、`Goal-v2.2.1-练习判题与如实补记.md`）的门槛全部继续有效。

## 1. 背景与目标
v2.2 删掉凑数后，阶段 12–24 的 45 课都过了数量门槛，但 Grok Bot 于 `eea0e93` 审计全部 217 个 `python run` 块，发现 **75 个弱示例**（见第 3 节 W1–W75）：
- 太短或没内容：有效代码不到 5 行，或只有 import/print（如 18.3 只打印版本号）；
- 报错演示只有 1–2 行，没有场景（如 `t[0] = 0`）；
- 课内或跨课近似重复（如 22.2 的两个 `validate_limit` 只差最后一行；20.2 与 20.3 的 `sum_squares`）；
- 同义反复或偏题：只断言自己刚写的字面量（阶段 16、17 大量出现）、`or True` 占位、和本课核心概念无关。
做完后：学习者在浏览器里点「运行」，每个示例都能看到一段说明本课概念的输出。

## 2. 范围
- 做：第 3 节表里列出的 75 个示例块所在课程（阶段 14–24）；`tests/check_course.py` 与 `tests/` 新测试（只收紧）；证据文件 `docs/规划/证据/v2.3-M<n>.txt`；`docs/规划/计划.md`；报告 `docs/规划/报告-v2.3-示例深化.md`。
- 不做：表外示例（除非为了消除重复必须连带改动，报告里逐个列出）；练习题；网站外观；阶段 01–11；重写 git 历史。不读 `.env`、`.private/`、`docs/private`。

## 3. 弱示例清单（Grok Bot 审计，全部必须改写）
「第几个 run 块」= 该课中第几个 ```` ```python run ```` 块（含 `raises=`），起始行以 `eea0e93` 为准。

| # | 课 | 文件 | 第几个 run 块 / 起始行 | 问题 | 现状摘录 |
|---|---|---|---|---|---|
| W1 | 14.1 | `14-文本文件与命令行/01-编码与bytes.md` | #2 / L38 | 有效代码 4 行（<5） | `buf = bytearray(b"abc") ⏎ buf[0] = ord("A") ⏎ print(bytes(buf)) ⏎ prin` |
| W2 | 14.1 | `14-文本文件与命令行/01-编码与bytes.md` | #3 / L51 | 有效代码 3 行（<5） | `bom = "\ufeff标题".encode("utf-8-sig") ⏎ plain = bom.decode("utf-8-sig")` |
| W3 | 14.1 | `14-文本文件与命令行/01-编码与bytes.md` | #4 / L61 | 报错演示只有 2 行，没有场景 | `bad = b"\xff\xfe" ⏎ bad.decode("utf-8")` |
| W4 | 14.1 | `14-文本文件与命令行/01-编码与bytes.md` | #5 / L66 | 有效代码 3 行（<5） | `bad = b"ok\xfftail" ⏎ print(bad.decode("utf-8", errors="replace"))   #` |
| W5 | 14.1 | `14-文本文件与命令行/01-编码与bytes.md` | #7 / L92 | 有效代码 3 行（<5）；只有 import/print | `import sys ⏎ print(sys.version_info[:2]) ⏎ print("defaultfilesystemenc` |
| W6 | 14.1 | `14-文本文件与命令行/01-编码与bytes.md` | #8 / L109 | 有效代码 2 行（<5） | `payload = "ok".encode("utf-8") ⏎ assert payload.decode("utf-8") == "ok` |
| W7 | 14.1 | `14-文本文件与命令行/01-编码与bytes.md` | #9 / L114 | 报错演示只有 1 行，没有场景 | `"a" + b"b"` |
| W8 | 14.2 | `14-文本文件与命令行/02-re正则.md` | #1 / L22 | 有效代码 4 行（<5） | `import re ⏎ m = re.search(r"\d+", "room temp=22C humidity=55") ⏎ print` |
| W9 | 14.2 | `14-文本文件与命令行/02-re正则.md` | #2 / L36 | 有效代码 3 行（<5）；只有 import/print | `import re ⏎ print(re.search(r"\n", "a\nb") is not None) ⏎ print(re.sea` |
| W10 | 14.2 | `14-文本文件与命令行/02-re正则.md` | #3 / L47 | 有效代码 3 行（<5） | `import re ⏎ pat = re.compile(r"[A-Z]{2,}") ⏎ print(pat.findall("GET /a` |
| W11 | 14.2 | `14-文本文件与命令行/02-re正则.md` | #6 / L89 | 有效代码 3 行（<5） | `import re ⏎ m = re.search(r"(\d{4}-\d{2}-\d{2})\s+(\w+)", "2026-01-01 ` |
| W12 | 14.2 | `14-文本文件与命令行/02-re正则.md` | #7 / L105 | 有效代码 4 行（<5） | `import re ⏎ line = "2026 INFO ok" ⏎ print(re.match(r"INFO", line)) ⏎ p` |
| W13 | 16.1 | `16-工具链与项目结构/01-src布局与pyproject.md` | #2 / L65 | 只断言自己刚写的字典字面量（同义反复），没演示依赖分组 | `groups = { ⏎ "dev": ["pytest", "ruff", "mypy"], ⏎ "data": ["numpy", "p` |
| W14 | 16.1 | `16-工具链与项目结构/01-src布局与pyproject.md` | #3 / L94 | 有效代码 3 行（<5） | `config = {"testpaths": ["examples/项目", "tests"], "python_files": ["tes` |
| W15 | 16.2 | `16-工具链与项目结构/02-ruff.md` | #1 / L25 | 有效代码 4 行（<5） | `items = [1, 2, 3] ⏎ total = sum(items) ⏎ assert total == 6 ⏎ print("st` |
| W16 | 16.2 | `16-工具链与项目结构/02-ruff.md` | #2 / L50 | 有效代码 4 行（<5） | `import math ⏎ def circle_area(r: float) -> float: ⏎ return math.pi * r` |
| W17 | 16.2 | `16-工具链与项目结构/02-ruff.md` | #3 / L72 | 有效代码 3 行（<5） | `rules = {"scripts/*": ["E501"], "tests/check_course.py": ["E501"]} ⏎ a` |
| W18 | 16.2 | `16-工具链与项目结构/02-ruff.md` | #4 / L87 | 有效代码 3 行（<5） | `pipeline = ["ruff check", "pytest"] ⏎ assert pipeline[0].startswith("r` |
| W19 | 16.3 | `16-工具链与项目结构/03-mypy.md` | #1 / L20 | 有效代码 4 行（<5） | `def greet(name: str) -> str: ⏎ return f"hi, {name}" ⏎ print(greet("py"` |
| W20 | 16.3 | `16-工具链与项目结构/03-mypy.md` | #2 / L32 | 有效代码 3 行（<5） | `def add(a: int, b: int) -> int: ⏎ return a + b ⏎ assert add(1, 2) == 3` |
| W21 | 16.3 | `16-工具链与项目结构/03-mypy.md` | #4 / L78 | 有效代码 2 行（<5） | `checks = {"pytest": "behavior", "mypy": "types"} ⏎ assert checks["mypy` |
| W22 | 16.3 | `16-工具链与项目结构/03-mypy.md` | #5 / L91 | 有效代码 4 行（<5） | `from typing import Any ⏎ def first_key(d: dict[str, Any]) -> str: ⏎ re` |
| W23 | 16.4 | `16-工具链与项目结构/04-logging配置与pdb.md` | #4 / L76 | 有效代码 3 行（<5） | `commands = {"n": "next", "s": "step", "c": "continue", "p": "print exp` |
| W24 | 17.1 | `17-打包与发布/01-wheel与构建后端.md` | #1 / L22 | 有效代码 4 行（<5） | `name = "logstats_pkg-0.1.0-py3-none-any.whl" ⏎ assert name.endswith(".` |
| W25 | 17.1 | `17-打包与发布/01-wheel与构建后端.md` | #2 / L60 | 有效代码 3 行（<5） | `backend = "hatchling.build" ⏎ assert backend.endswith(".build") ⏎ prin` |
| W26 | 17.1 | `17-打包与发布/01-wheel与构建后端.md` | #3 / L78 | `or True` 占位断言，恒为真，没演示包结构 | `import importlib.util ⏎ from pathlib import Path ⏎ pkg = Path("logstat` |
| W27 | 17.1 | `17-打包与发布/01-wheel与构建后端.md` | #4 / L98 | 报错演示只有 2 行，没有场景 | `from pathlib import Path ⏎ Path("dist/nonexistent.whl").read_bytes()` |
| W28 | 17.2 | `17-打包与发布/02-版本与入口脚本.md` | #2 / L56 | 有效代码 4 行（<5） | `entry_points = {"logstats": "logstats_pkg.cli:console_main"} ⏎ module,` |
| W29 | 17.2 | `17-打包与发布/02-版本与入口脚本.md` | #3 / L67 | 有效代码 4 行（<5） | `version = "0.1.0" ⏎ parts = version.split(".") ⏎ assert len(parts) == ` |
| W30 | 17.2 | `17-打包与发布/02-版本与入口脚本.md` | #4 / L82 | 有效代码 2 行（<5） | `modes = ["module", "editable", "uv-run"] ⏎ assert "editable" in modes` |
| W31 | 17.2 | `17-打包与发布/02-版本与入口脚本.md` | #5 / L95 | 有效代码 4 行（<5） | `def bad_main(): ⏎ return None ⏎ code = bad_main() ⏎ assert code is Non` |
| W32 | 17.3 | `17-打包与发布/03-发布流程.md` | #1 / L30 | 有效代码 3 行（<5） | `steps = ["test", "build", "check", "upload-testpypi", "smoke-install"]` |
| W33 | 17.3 | `17-打包与发布/03-发布流程.md` | #2 / L45 | 有效代码 2 行（<5） | `repos = {"testpypi": "practice", "pypi": "production"} ⏎ assert repos[` |
| W34 | 17.3 | `17-打包与发布/03-发布流程.md` | #3 / L59 | 有效代码 4 行（<5） | `secret = "pypi-token" ⏎ assert "token" in secret ⏎ assert not secret.s` |
| W35 | 17.3 | `17-打包与发布/03-发布流程.md` | #4 / L71 | 有效代码 2 行（<5） | `course_goal = "local wheel + pytest green" ⏎ assert "local" in course_` |
| W36 | 18.2 | `18-并发/02-multiprocessing与futures.md` | #1 / L22 | 有效代码 4 行（<5） | `from concurrent.futures import Future ⏎ fut: Future[int] = Future() ⏎ ` |
| W37 | 18.2 | `18-并发/02-multiprocessing与futures.md` | #2 / L40 | 只是列表推导，和执行器 / map 保序无关 | `def fetch_label(url: str) -> str: ⏎ return f"body:{url}" ⏎ urls = ["c"` |
| W38 | 18.2 | `18-并发/02-multiprocessing与futures.md` | #3 / L96 | 有效代码 3 行（<5） | `logical_cpus = 4 ⏎ default_workers = min(32, logical_cpus + 4) ⏎ print` |
| W39 | 18.3 | `18-并发/03-free-threaded现状.md` | #1 / L24 | 有效代码 4 行（<5） | `import sys ⏎ vi = sys.version_info ⏎ print(vi.major, vi.minor, vi.micr` |
| W40 | 18.3 | `18-并发/03-free-threaded现状.md` | #3 / L93 | 讲协程对象，偏离 free-threaded 主题 | `import asyncio ⏎ import inspect ⏎ async def ping() -> str: ⏎ return "p` |
| W41 | 18.3 | `18-并发/03-free-threaded现状.md` | #4 / L131 | 报错演示只有 2 行，没有场景 | `policy = (3, 14) ⏎ assert policy < (3, 14), "官方已提供 free-threaded 选项，请读` |
| W42 | 19.1 | `19-asyncio/01-协程与事件循环.md` | #2 / L62 | 只打印类名不等于 int，看不出「协程需被 await」 | `async def answer() -> int: ⏎ return 7 ⏎ maybe = answer() ⏎ print(maybe` |
| W43 | 19.2 | `19-asyncio/02-gather与TaskGroup.md` | #1 / L46 | 有效代码 3 行（<5） | `import asyncio ⏎ g = asyncio.gather ⏎ print(g.__name__, g.__module__ =` |
| W44 | 19.2 | `19-asyncio/02-gather与TaskGroup.md` | #2 / L67 | 有效代码 3 行（<5） | `import sys ⏎ ok = sys.version_info >= (3, 11) ⏎ print(ok, hasattr(__im` |
| W45 | 19.2 | `19-asyncio/02-gather与TaskGroup.md` | #3 / L82 | 有效代码 2 行（<5） | `names = ["create_task", "gather", "TaskGroup"] ⏎ print("gather" in nam` |
| W46 | 19.3 | `19-asyncio/03-异步HTTP概念.md` | #1 / L23 | 函数直接 return 200，导入了 urllib 却没用，同义反复 | `import urllib.error ⏎ import urllib.request ⏎ def fetch_status_example` |
| W47 | 19.3 | `19-asyncio/03-异步HTTP概念.md` | #2 / L60 | 有效代码 3 行（<5）；只有 import/print | `import asyncio ⏎ import inspect ⏎ print(hasattr(asyncio, "to_thread"),` |
| W48 | 19.3 | `19-asyncio/03-异步HTTP概念.md` | #4 / L97 | 报错演示只有 2 行，没有场景 | `status = 200 ⏎ print(status.ok)` |
| W49 | 20.1 | `20-性能/01-timeit与cProfile.md` | #1 / L22 | 有效代码 4 行（<5） | `import timeit ⏎ t_list = timeit.timeit("sum(range(200))", number=50_00` |
| W50 | 20.1 | `20-性能/01-timeit与cProfile.md` | #4 / L80 | 有效代码 4 行（<5） | `import timeit ⏎ setup = "from math import sqrt" ⏎ stmt = "[sqrt(i) for` |
| W51 | 20.2 | `20-性能/02-复杂度与数据结构.md` | #1 / L22 | 有效代码 4 行（<5） | `items_list = list(range(5000)) ⏎ items_set = set(items_list) ⏎ target ` |
| W52 | 20.2 | `20-性能/02-复杂度与数据结构.md` | #4 / L77 | 与 20.3#3 近似重复 | `def sum_squares_slow(n: int) -> int: ⏎ return sum(i * i for i in range` |
| W53 | 20.2 | `20-性能/02-复杂度与数据结构.md` | #5 / L99 | 报错演示只有 2 行，没有场景 | `allowed = [] ⏎ assert 0 in allowed, "空列表不应包含任何业务键"` |
| W54 | 20.3 | `20-性能/03-常见优化.md` | #1 / L22 | 有效代码 3 行（<5） | `parts = [f"item-{i}" for i in range(100)] ⏎ joined = "".join(parts) ⏎ ` |
| W55 | 20.3 | `20-性能/03-常见优化.md` | #3 / L51 | 与 20.2#4 近似重复 | `def sum_squares_slow(n: int) -> int: ⏎ total = 0 ⏎ for i in range(n): ` |
| W56 | 20.3 | `20-性能/03-常见优化.md` | #4 / L71 | 有效代码 3 行（<5） | `def count_positive(stream) -> int: ⏎ return sum(1 for x in stream if x` |
| W57 | 21.1 | `21-数据/01-NumPy入门.md` | #3 / L101 | 有效代码 3 行（<5） | `from statistics import mean ⏎ temps = [22.0, 18.0] ⏎ print(mean(temps)` |
| W58 | 21.2 | `21-数据/02-pandas入门.md` | #4 / L110 | 报错演示只有 2 行，没有场景 | `row = {"city": "上海"} ⏎ _ = row["temp"]` |
| W59 | 21.3 | `21-数据/03-Jupyter.md` | #2 / L39 | 只是切前 n 行，与 Notebook 预览/单元格无关 | `RAW = "city,temp\n上海,22\n北京,18\n" ⏎ def preview_rows(text: str, n: int` |
| W60 | 21.3 | `21-数据/03-Jupyter.md` | #3 / L69 | 拼接字符串，与 Notebook 输出无关 | `chunks = ["图1: ", "柱状", " ", "完成\n"] ⏎ report = [] ⏎ for c in chunks: ` |
| W61 | 22.1 | `22-Web与API/01-HTTP与ASGI.md` | #2 / L42 | 有效代码 4 行（<5） | `def parse_request_line(line: str) -> tuple[str, str]: ⏎ method, path, ` |
| W62 | 22.1 | `22-Web与API/01-HTTP与ASGI.md` | #4 / L93 | 报错演示只有 2 行，没有场景 | `payload = {"city": "上海"} ⏎ _ = payload["summary"]` |
| W63 | 22.2 | `22-Web与API/02-FastAPI与Pydantic.md` | #2 / L81 | 与 22.2#3 近似重复 | `def validate_limit(limit: int) -> int: ⏎ if limit < 1 or limit > 100: ` |
| W64 | 22.2 | `22-Web与API/02-FastAPI与Pydantic.md` | #3 / L90 | 与 22.2#2 近似重复 | `def validate_limit(limit: int) -> int: ⏎ if limit < 1 or limit > 100: ` |
| W65 | 22.3 | `22-Web与API/03-测试API.md` | #2 / L56 | 与 22.3#3 近似重复 | `def parse_limit(raw: str) -> int: ⏎ try: ⏎ value = int(raw) ⏎ except V` |
| W66 | 22.3 | `22-Web与API/03-测试API.md` | #3 / L69 | 与 22.3#2 近似重复 | `def parse_limit(raw: str) -> int: ⏎ try: ⏎ value = int(raw) ⏎ except V` |
| W67 | 23.3 | `23-Agent实战/03-流式输出.md` | #5 / L96 | 报错演示只有 2 行，没有场景 | `import json ⏎ json.loads('{"a":')  # 故意不完整` |
| W68 | 24.1 | `24-Python内部/01-名字绑定与对象模型.md` | #1 / L21 | 有效代码 4 行（<5） | `a = [1, 2] ⏎ b = a ⏎ b.append(3) ⏎ print(a, b is a)` |
| W69 | 24.1 | `24-Python内部/01-名字绑定与对象模型.md` | #6 / L89 | 报错演示只有 2 行，没有场景 | `t = (1, 2, 3) ⏎ t[0] = 0` |
| W70 | 24.3 | `24-Python内部/03-内存与GC.md` | #5 / L80 | 有效代码 4 行（<5） | `import gc ⏎ gc.set_debug(0) ⏎ unreachable = gc.collect() ⏎ print(type(` |
| W71 | 24.4 | `24-Python内部/04-导入系统.md` | #1 / L21 | 有效代码 4 行（<5）；只有 import/print | `import sys ⏎ import json ⏎ print("json" in sys.modules) ⏎ print(sys.mo` |
| W72 | 24.4 | `24-Python内部/04-导入系统.md` | #3 / L44 | 有效代码 2 行（<5） | `pkg = {"run_tool": lambda name, **kw: kw.get("text", "")} ⏎ print(pkg[` |
| W73 | 24.4 | `24-Python内部/04-导入系统.md` | #4 / L52 | 有效代码 3 行（<5）；只有 import/print | `import sys ⏎ print(any("site-packages" in p for p in sys.path)) ⏎ prin` |
| W74 | 24.4 | `24-Python内部/04-导入系统.md` | #5 / L61 | 有效代码 3 行（<5） | `import importlib ⏎ math = importlib.import_module("math") ⏎ print(math` |
| W75 | 24.4 | `24-Python内部/04-导入系统.md` | #6 / L76 | 报错演示只有 2 行，没有场景 | `import importlib ⏎ importlib.import_module("definitely_not_a_real_modu` |

## 4. 量化验收门槛
- **改写质量（W1–W75 每一个）**：
  - 有效代码（非空、非注释）≥ 8 行；
  - 运行后打印可观察的输出，输出本身能说明本课概念（例如前后对比、计时比较、状态变化、异常消息内容）；`raises=` 报错演示要先搭一个真实场景，再触发异常，异常前至少打印 1 行状态；
  - 紧挨代码块写一段解释（≥ 2 句），说明输出说明了什么；
  - 必须在 Pyodide 里能跑（不许用线程、进程、网络；需要本地才能跑的改成 `python local` 不算完成该项，另写浏览器可跑的版本）。
- **新检查规则（`check_course.py`，阶段 12–24）**，每条都要有单元测试：
  - R1：`python run`（不带 `raises=`）有效代码 < 5 行 → 失败；
  - R2：`python run` 只有 import/print 语句 → 失败；
  - R3：`python run raises=…` 有效代码 < 3 行 → 失败；
  - R4：两个 `python run` 块（同课或跨课）去空白和注释后相似度 ≥ 0.85（`difflib.SequenceMatcher`）→ 失败；
  - R5：断言里出现 `or True`、`assert True` 这类恒真写法 → 失败。
- **不降级**：每课正文非空行 ≥ 150、`python run` ≥ 3、`python exercise`（不含 local）≥ 2，全部保持；`python run` 总数不少于 217。
- **全量**：`uv run python tests/check_course.py` 全过；`uv run pytest` 0 失败（≥ 53 + 新增 ≥ 5）；`uv run ruff check` 通过；`cd site && npm run build` 成功；`time perl -e 'alarm 900; exec @ARGV' -- npm --prefix site run verify` 15 分钟内 exit 0。

## 5. 禁止捷径（违反任一条 = 不合格，整轮打回）
1. 用脚本/模板批量生成正文、课程、测试、文档（生成脚本本身也不许留在仓库）。
2. 占位内容：「见官方文档」「TODO」「待补充」「略」、空函数、`pass`/`NotImplemented` 桩。
3. 放宽或删除断言、删测试、加 `skip`/`xfail` 让测试变绿。
4. 跳过测试或只跑部分测试就宣称通过。
5. 该真实的用 mock 冒充（真实模型调用、真实数据库、真实安装验收）。
6. 只改文档/报告就宣称功能完成。
7. 改检查脚本本身降低门槛。
8. 复制粘贴重复内容凑行数、凑数量。
9. 把多个里程碑攒到最后一次性分批提交（见第 7 节硬门槛）。
10. 「先失败」提交之后任何放宽检查的改动（阈值调大、扩大豁免、跳过某类块）。检查只许收紧；每一处检查改动都要在报告里逐条列出原因。
11. 改写时用同一个骨架换名字批量套用（如每个示例都是「定义函数 → assert → print ok」）；改写后的示例也要过 R4。

## 6. 先证明门槛有效（M1）
先只加 R1–R5 和单元测试，不动课程正文，跑 `uv run python tests/check_course.py`，贴出被判失败的块数和清单。R1–R5 报出的块必须覆盖第 3 节里所有因太短、只有 import/print、近似重复被列入的条目（人工列入的同义反复和偏题条目，R5 抓不到的可以不覆盖，但报告要写清楚）。把这次输出存成 `docs/规划/证据/v2.3-M1.txt`，和检查改动一起提交。

## 7. 执行方式与硬门槛

### 里程碑（按阶段分组，一个里程碑一次提交）
- M1 `test(课程): v2.3 M1 弱示例门禁（先失败）`：R1–R5 + 测试 + 证据。
- M2 `feat(课程): v2.3 M2 阶段 12–14 示例深化`：W1–W12（12 个）。
- M3 `feat(课程): v2.3 M3 阶段 15–17 示例深化`：W13–W35（23 个）。
- M4 `feat(课程): v2.3 M4 阶段 18–20 示例深化`：W36–W56（21 个）。
- M5 `feat(课程): v2.3 M5 阶段 21–24 示例深化`：W57–W75（19 个）。
- M6 `docs(规划): v2.3 M6 报告与计划状态`：全量门槛 + 报告。

每个里程碑的门禁命令：`uv run python tests/check_course.py -k <本组阶段目录前缀>`（如 `-k 14-`，按组逐个跑）、`uv run pytest -q`、`perl -e 'alarm 300; exec @ARGV' -- npm --prefix site run verify:pyodide -- <本组阶段前缀>`；M6 跑第 4 节全量五条命令。输出原样写进 `docs/规划/证据/v2.3-M<n>.txt`（开头写命令和开始时间），和本里程碑的改动一起提交。本组 R1–R5 必须清零后才能提交；其他组还没改的失败可以留到对应里程碑。

### 原样引用：知识库 Goal 标准第九节（硬门槛）

## 九、硬门槛：里程碑提交必须带本里程碑的门禁证据（2026-10-19）

> 起因：jdp-python v2.2 与 v2.2.1 连续把多个里程碑攒到最后一次性分批提交（v2.2 的 M2–M6 提交时间同为 07:56:40；v2.2.1 的 M2 `cbb5d65`、M3 `e2cf1bc` 同为 08:03:33），每个里程碑没有单独跑检查。写进「禁止捷径」也没拦住，所以改成可机器核对的硬门槛。

**规则（原样贴进每份多里程碑 goal 的第 4 节和第 7 节）：**

1. 每个里程碑提交之前，必须先跑**本里程碑自己的**门禁命令；输出原样保存到证据文件（如 `docs/规划/证据/<版本>-M<n>.txt`，开头写命令和开始时间），并且**和该里程碑的改动放在同一次提交里**。没有证据文件的里程碑提交 = 不合格。
2. 相邻两个里程碑提交的提交时间间隔 **< 60 秒 = 自动不合格**，整轮打回，不讨论理由。
3. 不许改写历史来补救（rebase、amend、force-push 都不行）；已发生的违规只能在报告里如实写明。

**验收方法（Grok Bot）：**

```bash
git log --reverse --format='%h %ci %s' <goal提交>..HEAD
```

- 逐行算相邻里程碑提交的时间差，任一 < 60 秒判不合格；
- `git show --stat <每个里程碑提交>` 必须含本里程碑的证据文件，且证据里的命令与该里程碑的门禁一致、时间早于提交时间。

## 8. 硬停止条件
需要密钥、付费、真实发布、删除整课或 v1 内容、需要重写 git 历史：记入 `docs/规划/计划.md`，提交推送后停。

## 9. 默认决策
| 问题 | 默认 | 理由 |
| 弱示例其实应该删掉 | 不删，改写成好示例；`python run` 总数不许减少 | 不降级 |
| 两个近似重复的示例 | 两个都改写，各讲一个不同的点（如一个讲正常路径，一个讲边界与错误消息） | 消除重复 |
| 阶段 16、17 讲工具（ruff、mypy、打包）在浏览器里跑不了真工具 | 用标准库在浏览器里演示同一个原理（如用 `ast` 找未使用导入、用 `tomllib` 解析真实的 `pyproject` 片段、用 `zipfile` + `io.BytesIO` 构造并读取 wheel 的 `METADATA`、用 `importlib.metadata` 风格的 entry point 字符串解析并调用） | 真演示，不同义反复 |
| 计时示例结果不稳定 | 打印相对比较（倍数）并给宽松但有意义的断言 | 防偶发失败 |

## 10. 证据式最终报告（`docs/规划/报告-v2.3-示例深化.md`，并在最后一条回复里原样给出）
- 逐项表：W1–W75 每一项 → 改写后有效行数 → 输出要点 → 所在提交；
- 第 4 节每条门槛 → 实际值 → 证据；
- 原样贴：M1 先失败输出、全量五条命令末 10 行（verify 带 `time`）、`git log --reverse --format='%h %ci %s' <本 goal 提交>..HEAD`，并算出相邻里程碑提交的间隔（秒）；
- 检查改动逐条说明；
- 已知缺口：如实写，不准粉饰。

## 11. 通用规则
`git pull --ff-only`；只 add 自己改的文件；中文提交信息；推送 main；禁止 force-push；不读 `.env`/`.private/`/`docs/private`；不打印密钥值。M1 没有 `timeout`，限时用 `perl -e 'alarm N; exec @ARGV' -- <命令>`；`rg` 会卡住，搜索用 `git grep`。
