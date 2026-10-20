# Goal：修复 CI（main 分支 #9–#28 持续失败）

更新：2026-10-20。

## 1. 背景与根因（已核实）

- 失败工作流：`.github/workflows/ci.yml`，job `verify`，步骤「`node scripts/serve.mjs --port 5180 &` … `npm run smoke`」。
- 错误行：`✗ 首页路线图渲染 11 个阶段: 阶段卡片数 24`，`冒烟测试：10/11 通过`，`exit code 1`。
- 起点：CI #9（`704d741`，2026-10-18 23:24 北京时间），即 Goal v2 把课程从 11 个阶段扩到 24 个阶段（`50606fd`…`c6c4e8f`）后首次推送；#8（`1f5e56d`）仍为成功。
- 原因：`site/scripts/smoke.mjs` 第 46–50 行把阶段数硬编码为 11，未随课程扩展更新。其余步骤（unittest 30 个、check_course、verify:pyodide、build）在 #28 均通过。

## 2. 目标

CI 在 main 上恢复绿色，且冒烟测试仍能发现路线图渲染缺失。

## 3. 里程碑

- **C1 修冒烟断言**：阶段数不再硬编码，改为从课程数据源（路线图/侧边栏配置或 `docs/课程/` 下阶段目录）推导期望值，并与页面 `.roadmap-card` 数量比对；同步更新步骤名称。单独提交。
- **C2 本地复现 CI**：按 `ci.yml` 顺序在本机执行全部命令：`uv run --locked python -m unittest discover -s tests -p "test_*.py"`、`uv run --locked python tests/check_course.py`、`site/` 下 `npm ci`、`npm run verify:pyodide`、`npm run build`、起 `node scripts/serve.mjs --port 5180` 后 `npm run smoke`。全部通过才可推送。
- **C3 推送并确认**：`git pull --ff-only` 后 push；用 `gh run list --workflow CI --branch main -L 1` / `gh run watch` 确认该提交的 CI 结论为 `success`，失败则 `gh run view --log-failed` 定位并回到 C1。
- **C4 报告**：在 `docs/规划/计划.md` 记录提交号与 CI run 编号/链接。

## 4. 禁止捷径

- 不得删除、跳过、注释掉测试或 CI 步骤，不得 `continue-on-error`，不得把期望值改成写死的 24。
- 一项修复一个提交；只 stage 明确路径；不改写历史；先 `pull --ff-only` 再 push；`NO_PROXY=127.0.0.1,localhost`。
- 不读取、不打印 `.env*`、`.private/`、`docs/private`。

## 5. 完成标准

GitHub 上该提交的 CI run 为 success（附链接），本地五步命令输出附在报告中。未看到 success 不得声称完成。
