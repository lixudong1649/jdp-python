# jdp-python v2.4 Goal：代码解读首版（选一段 Python，讲清语法、结构、怎么跑、易错点，并链到课程）

> 编写：2026-10-19（Asia/Shanghai），Grok Bot，按知识库《Goal 提示词编写与验收标准》（`jiudingpeng/docs/project/个人生态/Goal提示词编写与验收标准.md`）。
> 模型：**composer-2.5**（asahi 额度规则：只用 composer-2.5，不用 opus；同一仓库同时只跑一个 agent）。
> 设计依据（必须先通读）：[代码解读与AI助手-规划设计.md](代码解读与AI助手-规划设计.md)，下文简称「设计」。设计第 8 节待决 Q1–Q5 全部按「默认做法」执行。
> 基线：开工时的 `git rev-parse --short HEAD`，写进 M0 证据。

## 1. 背景与目标

asahi 问：「jdp-python 可以增加一个类似解释代码的能力么？比如我选择一个 Python 文件，让它帮看一下语法、含义、有啥功能。」

本课程的终点就是读懂代码，`docs/代码解读/minimal_agent.md` 已经是一份手写的解读（22 行语法表）。本轮把它变成对任意 Python 代码都能用的功能：

- **第 1 层（必做）**：浏览器内 Pyodide 用标准库 `ast` 分析，输出设计 4.2 节的 6 栏结果，每项链到本课程的课、术语表和练习。零费用、离线、GitHub Pages 可用。
- **第 2 层（必做，但默认关闭、只在本机）**：AI 讲解，本机服务 + 默认 Ollama `qwen2.5-coder:7b`。

做完后：asahi 打开 `http://127.0.0.1:5180/代码解读/`，粘贴或选一个文件，1 次点击得到解读；在任一课程代码块上点「解读」也能直达。

## 2. 范围

**做（in）：**

- `site/public/py-explain.py`（新）：浏览器与 CPython 共用的分析器，只分析、不执行代码。
- `docs/代码解读/概念索引.md`（新）：概念 → AST 节点或规则 → 含义 → 课程链接 → 术语表链接；`docs/代码解读/index.md`（新）：代码解读页。
- 站点：`CodeExplainer.vue`（新）、Worker 增加分析消息类型、`PyRunner` 加「解读」按钮、`lib/` 构建期解析概念索引、侧边栏与导航入口。
- `scripts/explain_server.py`（新，第 2 层）：只用标准库 `http.server` + `urllib`，监听 127.0.0.1；`scripts/dev.sh` 增加 `explain start|stop|status`。
- `tests/check_explain.py`（新）、`tests/test_explain_*.py`（新）、`evals/code-explain-v1.jsonl`（新，20 题）、冒烟测试增补。
- 文档：README、`docs/项目架构与技术栈.md`、CHANGELOG、`docs/规划/计划.md` 加 v2.4 一节、`.env.example` 增加变量名（不填值）。

**不做（out）：**

- 不改任何课程正文的教学内容（只允许在 `docs/代码解读/` 新增文件、在 `docs/index.md` 和 README 加入口链接）；
- 不改 `py-runtime.py` 的执行与判题行为；
- 不做问答助手、逐步执行视图（设计第 5、6 节的 v2.5、v2.6）；
- 不在 GitHub Pages 构建里出现 AI 按钮；不接 jdp-rag、不碰其他仓库；
- 不引入新的 npm 或 Python 依赖（CodeMirror、Pyodide、Vue 现有即可；服务端只用标准库）；
- 不监听 127.0.0.1 以外的地址。

## 3. 交付物清单

| 编号 | 交付物 | 数量 | 位置 |
| --- | --- | --- | --- |
| D1 | 分析器 | 1 个文件，输出固定 JSON 结构（概览、语法点、结构、概念、运行、易错点），附 JSON Schema | `site/public/py-explain.py`、`site/public/py-explain.schema.json` |
| D2 | 概念索引 | ≥ 60 个概念，每个都有课程链接 | `docs/代码解读/概念索引.md` |
| D3 | 易错点规则 | ≥ 10 条，每条有说明、Ruff 规则对照（有的话）、课程链接 | `py-explain.py` + 概念索引「易错点」表 |
| D4 | 页面与组件 | 代码解读页 1 个；4 种输入（粘贴、选仓库示例、打开本机文件、课程块「解读」按钮） | `docs/代码解读/index.md`、`site/.vitepress/theme/components/` |
| D5 | AI 讲解服务 | 1 个本机服务，`/v1/health`、`/v1/explain` 两个接口 | `scripts/explain_server.py` |
| D6 | 金标样例 | ≥ 20 份「代码 → 期望结果」样例，含 minimal_agent.py | `tests/fixtures/explain/` |
| D7 | 测试与检查 | 新测试函数 ≥ 60 个；`check_explain.py` ≥ 25 项检查 | `tests/` |
| D8 | AI 评测题 | 20 题（≥ 6 道来自练习题，用于检查不泄答案） | `evals/code-explain-v1.jsonl` |
| D9 | 截图 | after ≥ 6 张（空页、结果页、语法错误、课程块按钮、深色、390 宽） | `docs/规划/证据/v2.4-screenshots/` |
| D10 | 证据与报告 | M0–M6 每个里程碑一个证据文件，加最终报告 | `docs/规划/证据/`、`docs/规划/报告-v2.4-代码解读首版.md` |

## 4. 量化验收门槛

**分析器（`check_explain.py` 机器检查）：**

- E01 语料 = 全部 397 个 `python run` 块 + 175 道练习（浏览器 172 + 本地 3）的 solution + `examples/` 下 29 个 `.py`（数量以 M0 时实际统计为准并写进证据）。分析器在全部语料上 **0 崩溃**，每份都输出通过 D1 Schema 校验的 JSON，且语法点 ≥ 1 条。
- E02 **CPython 与 Pyodide 一致**：同一份语料，`uv run python` 与 Node 里的 Pyodide（沿用 `verify-pyodide.mjs` 的做法）输出的 JSON 逐字节相同，一致率 100%。
- E03 **对照手写解读**：对 `examples/agent/minimal_agent.py`，`docs/代码解读/minimal_agent.md` 第 1 节表格的 22 行里，分析器命中 ≥ 20 行，且命中行的行号与表中一致（表中行号若已过期，以当前文件为准并在报告里列出差异）。
- E04 **概念覆盖**：语料中出现的不同 AST 节点种类，≥ 95% 映射到概念索引里的概念；未映射的逐个列出。
- E05 **链接全有效**：概念索引里每个课程链接、术语表链接、练习 id 都真实存在（文件存在、锚点存在、练习 id 存在）；失效数 = 0。
- E06 **易错点**：≥ 10 条规则，每条 ≥ 2 个应命中样例 + ≥ 2 个不应命中样例，全部判对；在 397 个示例上的命中次数逐条列出，并人工复核前 20 条命中（报告附表）。
- E07 **不执行代码**：分析器源码里不出现 `exec`、`eval`、`compile(` 用于执行、`__import__`、`importlib`、`subprocess`、`os.system`；用一段 `import os; os.remove(...)` 的样例证明分析后文件仍在。
- E08 **语法错误**：10 个错误样例都返回出错行号、列号和中文提示，不抛异常。
- E09 **性能**：在 Node + Pyodide 中预热后，3000 行文件分析 ≤ 1.5 秒，minimal_agent.py ≤ 150 毫秒（各跑 20 次取 P95）。

**页面（冒烟测试，Playwright + 本机 Chrome）：**

- U01 代码解读页 4 种输入都能出结果；6 栏都渲染；概念链接点击后进入对应课。
- U02 每个 `python run` 块都有「解读」按钮（抽 10 个课页面检查），点击后代码原样带到解读页。
- U03 打开本机文件与分析过程中，页面**没有**发往 127.0.0.1:5180 以外的请求（拦截并计数 = 0；AI 讲解关闭时）。
- U04 深色模式、390 宽两种状态无横向滚动条；输入框都有 `<label>`。
- U05 GitHub Pages 构建（`SITE_BASE=/jdp-python/`）产物里**没有** AI 讲解按钮的 DOM（检查构建后的 HTML 与 JS 中的标记字符串）；本机且服务可达时才显示。

**AI 讲解（第 2 层）：**

- A01 服务只监听 127.0.0.1（`lsof` 证明）；默认不启动；`/v1/health` 返回模型名和是否就绪，不含任何密钥。
- A02 20 题全部真实调用本机 Ollama `qwen2.5-coder:7b`（不许 mock）：
  - 输出通过 Schema 校验的比例 = 100%（允许服务内最多 1 次重试，次数记入报告）；
  - 页面最终展示的课程链接全部来自第 1 层结果（模型自造的链接被丢弃，丢弃次数记入报告），有效率 = 100%；
  - 每题预写 3–5 个要点关键词，要点命中率平均 ≥ 70%（如实报告，不达标不许改题）；
  - 6 道练习题：输出与参考答案的规范化代码相似度（`difflib.SequenceMatcher` 比 token 序列）全部 < 0.6，且不出现参考答案中的完整函数体。
- A03 限额：输入 > 400 行返回 413 和中文提示；超时 60 秒返回 504；每日上限（`JDP_PYTHON_EXPLAIN_DAILY_LIMIT`，默认 200）用测试改成 3 验证第 4 次返回 429；同一输入第二次命中缓存（不再调用模型，计数证明）。
- A04 日志与报错里不出现密钥值（设一个已知测试值断言不出现）、不出现完整用户代码（只记哈希和行数）。

**代码质量（沿用本仓现有命令）：**

- C01 `uv run python tests/check_course.py` exit 0（课程原有检查一条不改）。
- C02 `cd site && npm run verify:pyodide` exit 0；`npm run build` exit 0；`npm run smoke` exit 0。
- C03 `uv run pytest` 全量 0 失败；`uv run ruff check .` 0 个问题。
- C04 `uv run python tests/check_explain.py` exit 0；`--live`（含 A02）也 exit 0。

**第九节原样：**

1. 每个里程碑提交之前，必须先跑**本里程碑自己的**门禁命令；输出原样保存到证据文件（如 `docs/规划/证据/<版本>-M<n>.txt`，开头写命令和开始时间），并且**和该里程碑的改动放在同一次提交里**。没有证据文件的里程碑提交 = 不合格。
2. 相邻两个里程碑提交的提交时间间隔 **< 60 秒 = 自动不合格**，整轮打回，不讨论理由。
3. 不许改写历史来补救（rebase、amend、force-push 都不行）；已发生的违规只能在报告里如实写明。

本项目的证据文件路径定为 `docs/规划/证据/v2.4-M<n>.txt`（与 v2.3.x 相同）。文件开头写：命令、开始时间、`git rev-parse --short HEAD`。每条命令后写 `exit=<码>`。

## 5. 禁止捷径（违反任一条 = 不合格，整轮打回）

1. 用脚本/模板批量生成正文、课程、测试、文档（生成脚本本身也不许留在仓库）。
2. 占位内容：「见官方文档」「TODO」「待补充」「略」、空函数、`pass`/`NotImplemented` 桩。
3. 放宽或删除断言、删测试、加 `skip`/`xfail` 让测试变绿。
4. 跳过测试或只跑部分测试就宣称通过。
5. 该真实的用 mock 冒充（真实模型调用、真实数据库、真实安装验收）。
6. 只改文档/报告就宣称功能完成。
7. 改检查脚本本身降低门槛。
8. 复制粘贴重复内容凑行数、凑数量。

本项目补充：

9. 概念索引的「含义」一列逐条手写，一句话讲清，不许从别处整段复制；课程链接必须指向真正讲这个概念的课（报告里抽 15 条附「概念 → 课 → 该课中讲它的小节标题」）。
10. 金标样例的期望结果手写后再跑分析器比对，不许先跑分析器再把输出存成期望值。
11. 页面显示的行号、数量都来自分析器 JSON，不许在模板里写死。
12. A02 的要点关键词在第一次调用模型**之前**写好并提交（M5 里先提交题，再跑模型；题目提交与评测结果不在同一次提交里也可以，但都要在 M5 时间段内，且题目提交在前）。
13. 报告里的每个数字都从本轮证据文件原样抄。

## 6. 先证明门槛有效（M0）

先写 `tests/check_explain.py`，把第 4 节 E01–E09、U05、A01–A04 能机器检查的都写进去（U01–U04 写进冒烟测试）。在**还没写分析器**的 HEAD 上运行，证明 E01、E03、E04、E05、E06 判 FAIL；原样贴出 FAIL 的条目和条数，存到 `docs/规划/证据/v2.4-M0.txt`。同时把语料统计（397 / 175 / 29 的实际数）写进证据。

## 7. 执行方式

一次跑完 M0–M6，中途不停、不提问。每个里程碑都要做到：

- 先完成本里程碑的改动；
- **当场**跑本里程碑的门禁命令，输出存 `v2.4-M<n>.txt`；
- 与改动一起提交，提交信息写 `v2.4-M<n>: <说明>`；
- 然后 `git pull --ff-only && git push origin main`。

每次只 `git add` 本里程碑的文件，禁止 `git add -A`。

| 里程碑 | 内容 | 本里程碑门禁（至少） |
| --- | --- | --- |
| M0 | `check_explain.py`、金标样例目录、语料统计、证明当前 FAIL | `check_explain.py`（预期 exit≠0，贴 FAIL 清单）；`check_course.py` 仍 exit 0 |
| M1 | 分析器核心：概览、语法点、结构、运行、语法错误；Schema | E01、E07、E08；新增 pytest；ruff |
| M2 | 概念索引 + 易错点规则 + 金标样例 | E03、E04、E05、E06；pytest |
| M3 | Pyodide 接入（Worker 消息类型）+ 代码解读页 + 4 种输入 | E02、E09；`npm run build`；U01、U03、U04 |
| M4 | 课程块「解读」按钮、导航入口、Pages 构建检查 | U02、U05；`npm run smoke`；`check_course.py` |
| M5 | AI 讲解服务、`dev.sh explain`、评测题（先提交题）、真实评测 | A01–A04；`check_explain.py --live` |
| M6 | 全量门禁、截图、README / 架构 / CHANGELOG / 计划 / `.env.example`、最终报告 | 第 4 节全部：`uv run python tests/check_course.py`、`uv run pytest`、`uv run ruff check .`、`uv run python tests/check_explain.py`、`uv run python tests/check_explain.py --live`、`cd site && npm run verify:pyodide && npm run build && npm run smoke`；`git status` 干净 |

**环境注意（M1 本机）：**

- 本机有 Clash 系统代理（127.0.0.1:7890）。访问本机服务一律绕过代理：Python `urllib` 用 `ProxyHandler({})`，curl 用 `--noproxy '*'`，Chrome 加 `--no-proxy-server`。
- 跑任何命令前先 `export NO_PROXY=127.0.0.1,localhost no_proxy=127.0.0.1,localhost`。
- 冒烟测试与临时服务用临时端口（站点用 `JDP_PYTHON_SITE_PORT` 指定 18000–18999 之间的空闲端口，AI 服务同理）；**不碰 5180 上正在运行的站点**，用完关掉临时进程（报告贴 `lsof -iTCP -sTCP:LISTEN -n -P | grep -E 'node|python'`）。
- Ollama 用本机已有的 `127.0.0.1:11434`，只用 `qwen2.5-coder:7b`，不拉新模型。
- 交互 shell 是 zsh，多参数命令写成 bash 脚本再执行；`rg` 会卡住，用 `git grep`；不同时跑两个 pytest。

## 8. 硬停止条件（只有这些才停下来问）

涉及密钥/凭据、付费、真实发布（PyPI、应用商店、公网上线）、破坏性删除（删功能、删数据、删旧代码）、只能 asahi 拍板的决定。

本项目明确如下：

- 读取 `.env`、打印任何密钥的值：一律禁止。服务运行时由程序读取 `.env` 可以，但 agent 不许打开或打印它。
- 需要调用 DeepSeek 等付费模型才能完成门槛：停下（本轮只用本机 Ollama）。
- 需要新增 npm 或 Python 依赖：停下。
- 需要改课程正文教学内容或 `py-runtime.py` 行为：停下。

## 9. 默认决策（代替提问）

| 问题 | 默认做法 | 理由 |
| --- | --- | --- |
| 设计第 8 节 Q1–Q5 | 全部按「默认做法」执行 | asahi 未回复前按保守做法 |
| AI 服务端口 | `JDP_PYTHON_EXPLAIN_PORT`，默认 8031；测试一律用临时端口 | 设计 Q3 |
| AI 服务提供方 | `JDP_PYTHON_EXPLAIN_PROVIDER=ollama`（默认）；`deepseek` 分支代码可写，但本轮不实测、报告如实写「未实测」 | 不花钱 |
| 浏览器里没有的第三方包 | 以 Pyodide 314.0.7 自带包清单 + 标准库判断「能否在浏览器运行」，清单来源写进报告 | 不编造 |
| 课程块「解读」按钮带代码的方式 | `sessionStorage` 传递，URL 只带一个随机键；不把代码放进 URL | URL 会进历史记录 |
| AI 讲解的提示词 | 系统提示 ≤ 400 字，写进 `scripts/explain_prompt.md` 并带版本号；缓存键包含版本号 | CS50「指令稀释」教训 |
| 本表外的小分歧 | 选保守、可回退的做法，记入最终报告 | |

## 10. 证据式最终报告（必须）

写到 `docs/规划/报告-v2.4-代码解读首版.md`：

- 逐项表：E01–E09、U01–U05、A01–A04、C01–C04、D1–D10 → 实际数值 → 证据（文件路径和行号、命令输出原样）。
- 跑过的命令及结果（原样贴关键输出），每个数字都从证据文件抄。
- 提交哈希列表，附 `git log --reverse --format='%h %ci %s' <基线>..HEAD`，并算出相邻提交的时间间隔。
- E03 对照表：手写表 22 行 → 是否命中 → 行号。
- A02 逐题表：题号、Schema 是否通过、重试次数、丢弃的链接数、要点命中、练习相似度。
- 截图清单。
- 已知缺口：如实写，不准粉饰（例如 7B 模型讲解质量的真实情况）。

## 11. 通用规则

- git：`git pull --ff-only`；只 add 自己改的文件，不提交别人未提交的改动；禁止 force-push；本仓库推送 `main`。
- 网页项目：统一页脚（版权方 `lixudong1649`，授权与 LICENSE 一致），沿用现有页脚。
- 密钥：只放项目自己的 `.env`（gitignore、600 权限），从总库经 secrets-sync 同步；不另存、不打印值、不写进日志和提交。
