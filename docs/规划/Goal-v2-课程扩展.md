# Goal v2：课程扩展到 L2–L6（一次执行完）

## 目标
按 `docs/规划/规划.md` 第 2 节，一次完成阶段 12–24 的全部课程、练习、阶段项目和测试，并同步更新学习路线、课程大纲、首页、索引和站点，最后提交并推送 main。

## 必读
`docs/规划/规划.md`、`docs/课程大纲.md`（单课模板、判题约定）、`docs/项目架构与技术栈.md`、`tests/check_course.py`、任意一课（如 `docs/课程/10-读代码技巧/02-装饰器.md`）作为格式样板。

## 要做
1. 新建 `docs/课程/12-…` 到 `24-…` 目录，每阶段有 `index.md` 导读，课名按规划表，每阶段 3–4 课，严格用 v1 单课模板（目标/核心概念/易错点/对照/读代码/练习/小结/延伸阅读）。
2. 能在 Pyodide 中运行的示例用 `python run`，练习用 `python exercise`。依赖第三方库或多进程、网络、文件系统的示例用普通 `python` 块，并在 `examples/项目/` 里放可运行版本。
3. 阶段项目放 `examples/项目/NN-名称/`，每个都带 pytest 测试。第三方依赖（pytest、ruff、mypy、numpy、pandas、fastapi、httpx 等）用 `uv add --group` 放进开发或可选依赖组。
4. `tests/check_course.py` 的 `ALLOWED_DOMAINS` 只加这些库的官方文档域名（如 docs.pytest.org、docs.astral.sh 已有、mypy.readthedocs.io、numpy.org、pandas.pydata.org、fastapi.tiangolo.com、docs.pydantic.dev、jupyter.org）。不放宽其他规则。
5. 更新 `docs/学习路线.md`（追加阶段 12–24 小节，修改“不在本路线范围”说明）、`docs/课程大纲.md`（定位、结构表、前置关系、课数）、`docs/index.md`、附录速查表/术语表、站点首页路线图（`CourseRoadmap` 按 L 分层显示），页脚保持统一格式：`© 2026 lixudong1649`，附许可链接。
6. 版本表述以 2026-10-18 为核对日期：最新稳定版 3.15（2026-10-09 发布），3.10 已 EOL，free-threaded 3.14 起官方支持但非默认。项目仍固定 3.12，正文对 3.12–3.15 成立；新特性标“3.x 起”。
7. 完成后更新 `docs/规划/计划.md`（M1–M5 填日期和提交号）和 `CHANGELOG.md`。

## 验收（全部满足才算完成）
- `uv sync --all-groups`、`uv run python tests/check_course.py`、`uv run pytest`、`uv run ruff check`（项目代码）全部通过。
- `cd site && npm run build` 成功，`verify-pyodide.mjs` 通过（静态块除外）。
- 13 个新阶段都有 index 和课程，每课至少 1 道判题练习，每个阶段项目的测试都通过。
- 学习路线、大纲、首页与目录结构一致，没有死链。

## 约束
- 只引用官方来源。不读 `.env`、`.private/`，不写任何密钥。
- `git pull --ff-only`；只提交自己改的文件；按里程碑分几次提交，提交信息用中文；最后 `git push origin main`，禁止 force-push。
- 不删除、不改写 v1 已有课程的内容（只修链接、补交叉引用）。
- 不真发布到 PyPI。

## 默认做法（不要停下来问）
- 课程名称、练习细节自定，以规划表为准。
- 某个示例在 Pyodide 不能运行，就改成静态块，在本地项目验证。
- 第三方库用当前最新稳定版，锁进 uv.lock。

## 停止条件
- 验收全部通过并已推送，或者
- 遇到需要密钥、付费、真实发布，或必须删除 v1 内容的情况：停下，在 `docs/规划/计划.md` 记录卡点后提交推送。
