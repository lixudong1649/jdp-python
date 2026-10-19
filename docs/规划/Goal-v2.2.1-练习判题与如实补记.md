# jdp-python v2.2.1 修正 Goal：本地练习真判题、恢复练习门槛、如实补记

> 2026-10-19（北京时间）。按知识库《Goal 提示词编写与验收标准》第七节「打回」格式。原 goal：`docs/规划/Goal-v2.2-去凑数返工.md`、`Goal-v2.1-课程深化重写.md`，仍然全部有效。模型：composer-2.5。

## 1. 不合格项（附证据，Grok Bot 于 `222265a` 独立验收）
1. **`python local exercise` 没有被判题**：`tests/check_course.py::check_blocks` 先判断 `"run" in b.flags or "local" in b.flags`，于是 `local exercise` 被当成普通示例，把 starter+solution+check 三段拼在一起整体执行一次；没有「参考答案通过、起始代码被判失败」的判题。证据：`check_course.py` 与 `verify-pyodide` 的「练习参考答案通过」都是 169，3 道 local 练习（`s18-l01-thread`、`s18-l01-bump`、`s18-l03-safebox`）没有被计入。
2. **在「先失败」提交之后放宽了检查**（`git diff 7c2c755 HEAD -- tests/check_course.py`）：
   - 练习计数从 `python exercise` 改成 `python (?:local )?exercise`，把没判题的 local 练习也算进 ≥2 → 18.1 实际 0 道判题练习，18.3 只有 1 道；
   - `PYODIDE_FORBIDDEN_IN_RUN` 删掉了 `concurrent\.futures`；
   - 报告没写这两处改动。
3. **里程碑提交是假的逐个提交**：M2–M6（`e0065f7` `6760ed0` `e2fb46c` `5b517a1` `53d6b51`）在 07:56:39 同一条命令里一次性分批提交，提交时间都是 07:56:40。凑数是在 07:53:35 用一个脚本统一删掉的，每个里程碑没有单独跑检查。报告里没写。
4. `tests/test_check_course_v22.py::test_filler_marker_detected` 往 `docs/课程/12-数据模型与协议/` 里写探针文件 `99-gate-probe.md`，测试中断就会留在课程目录里。

## 2. 范围
- 做：`tests/check_course.py`、`tests/test_check_course_v22.py`、`site/scripts/verify-pyodide.mjs`（如需）、`docs/课程/18-并发/01-threading与GIL.md`、`03-free-threaded现状.md`（以及修好检查后其他不达标的课）、报告 `docs/规划/报告-v2.2-去凑数返工.md`（只追加）、`docs/规划/计划.md`。
- 不做：其他课程正文；网站外观；重写 git 历史（不 rebase、不 amend、不 force-push）。

## 3. 交付物与量化门槛
| 编号 | 交付物 | 门槛 |
| F1 | `check_blocks` 对 `python local exercise` 按练习判题：用本地解释器跑 solution+check 必须通过、starter+check 必须失败；id 参与查重 | 新增单元测试 ≥ 2 个（solution 失败 → 报错；starter 通过 → 报错），用 `tmp_path`/临时目录造课程文件；`check_course.py` 输出的「练习参考答案通过」= Pyodide 数 + local 练习数（贴两个数字） |
| F2 | 练习门槛恢复：每课 `python exercise`（浏览器可判题，不含 local）≥ 2；local 练习另计、不抵扣 | 阶段 12–24 共 45 课全部满足；把计数改回不含 local |
| F3 | 18.1、18.3 补齐浏览器可判题练习（手写、讲本课具体知识点，不依赖线程/进程，例：用生成器模拟线程交替与竞态、用假锁类讲临界区、按 `sys._is_gil_enabled` 是否存在分支的检测函数）；每道练习的 starter 必须被判失败 | 18.1 新增 ≥ 2 道、18.3 新增 ≥ 1 道；两课 `python exercise` 各 ≥ 2 |
| F4 | `concurrent.futures`：恢复禁止 `concurrent.futures` 的执行器用法，只放行单独用 `Future` 的块；写测试证明 `from concurrent.futures import ThreadPoolExecutor` / `ProcessPoolExecutor` / `as_completed` 配执行器在 run/exercise 里都会被判违规 | 测试 ≥ 1 个；当前课程 0 违规 |
| F5 | 探针测试改用临时目录，不写 `docs/课程` | 跑完 `git status --porcelain docs/课程` 为空 |
| F6 | 报告追加「v2.2 更正」小节：如实写不合格项 1–3（检查放宽了哪两处、M2–M6 是一次性分批提交、提交时间相同、凑数是统一删除的），以及本轮怎么修 | 原样贴 `git log --format='%h %ad %s' --date=format:%T 9e54b82..HEAD` |

全量门槛（不变）：`uv run python tests/check_course.py` 全过；`uv run pytest` 0 失败（≥ 48 + 本轮新增）；`uv run ruff check`；`cd site && npm run build`；`perl -e 'alarm 900; exec @ARGV' -- npm --prefix site run verify` 15 分钟内 exit 0。

## 4. 禁止捷径（违反任一条 = 不合格，整轮打回）
1. 用脚本/模板批量生成正文、课程、测试、文档（生成脚本本身也不许留在仓库）。
2. 占位内容：「见官方文档」「TODO」「待补充」「略」、空函数、`pass`/`NotImplemented` 桩。
3. 放宽或删除断言、删测试、加 `skip`/`xfail` 让测试变绿。
4. 跳过测试或只跑部分测试就宣称通过。
5. 该真实的用 mock 冒充（local 练习必须用真实本地解释器判题）。
6. 只改文档/报告就宣称功能完成。
7. 改检查脚本本身降低门槛——**本轮起检查只许收紧；任何检查改动都要在报告里逐条列出原因**。
8. 复制粘贴重复内容凑行数、凑数量。
9. 把多个里程碑攒到最后一次性分批提交。

## 5. 先证明门槛有效
先只改检查（F1、F2、F4、F5），不动课程，跑 `uv run python tests/check_course.py`，贴出：18.1、18.3 练习数不足的失败；local 练习被真正判题后的结果（如有 starter 竟然通过，照实贴）。单独提交 `test(课程): v2.2.1 M1 本地练习判题与练习门槛恢复（先失败）`。

## 6. 执行方式（每项改完 → 跑检查 → 立刻单独提交，再做下一项）
- M1 先失败（第 5 节）。
- M2 `feat(课程): v2.2.1 M2 18.1 浏览器可判题练习`。
- M3 `feat(课程): v2.2.1 M3 18.3 浏览器可判题练习`（若检查暴露其他课不达标，每课各一次提交）。
- M4 `docs(规划): v2.2.1 M4 报告更正与计划状态`，跑全量门槛。
每次提交前跑 `uv run python tests/check_course.py -k 18-` 和 `uv run pytest`。全部完成后 `git pull --ff-only`，推送 main。

## 7. 硬停止条件
需要密钥、付费、真实发布、删除整课或 v1 内容、需要重写 git 历史：记入 `docs/规划/计划.md`，提交推送后停。

## 8. 默认决策
| 问题 | 默认 | 理由 |
| local 练习在网站上怎么显示 | 保持「需在本地运行」，不出判题按钮 | Pyodide 跑不了线程 |
| 某 local 练习的 starter 判题时竟然通过 | 改 starter 或加强 check，使其真失败，写进报告 | 判题要有效 |

## 9. 证据式最终报告（追加到 `docs/规划/报告-v2.2-去凑数返工.md`，并在最后一条回复里原样给出）
逐项表 F1–F6 → 实际值 → 证据；原样贴先失败输出、全量五条命令末 10 行（verify 带 `time`）、本轮 `git log --format='%h %ad %s' --date=format:%T`；已知缺口如实写。

## 10. 通用规则
`git pull --ff-only`；只 add 自己改的文件；中文提交信息；推送 main；禁止 force-push；不读 `.env`/`.private/`/`docs/private`；不打印密钥值。没有 `timeout`，限时用 `perl -e 'alarm N; exec @ARGV' -- <命令>`；搜索用 `git grep`。
