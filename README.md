# jdp-python

## 项目定位

更新：2026-09-27。Python 专题实验仓，用于学习、探索、调研和测评。示例、实验记录与选型结果按主题保存；不作为生产服务或主产品能力交付承诺。当前目录内容不代表已完成所有实验。

2026-10-06 新增：面向有 JS/Java 经验开发者的中文 Python 课程与本地学习网站，见 [Python 课程与学习网站](#python-课程与学习网站2026-10-06-新增)。

作者：[lixudong1649](https://github.com/lixudong1649) · 反馈：[GitHub Issues](https://github.com/lixudong1649/jdp-python/issues) · 许可：代码 MIT，课程内容 CC BY-NC-SA 4.0（见 [许可与声明](#许可与声明)）

## 维护边界

- 每项实验记录目的、依赖、运行方式、结果与限制。
- 区分计划、已有文件和经过验证的能力。
- 不提交密钥、私人数据或无必要的临时产物。

## 目录

```text
README.md                      项目说明（本文件）
LICENSE / LICENSE-CONTENT.md   许可：代码 MIT / 课程内容 CC BY-NC-SA 4.0
CONTRIBUTING.md / CHANGELOG.md 反馈与贡献指南 / 更新记录
.github/workflows/             CI（校验与构建）、GitHub Pages 部署
pyproject.toml / uv.lock       依赖声明与锁定（uv 管理）
.python-version                固定 Python 版本（3.12）
.env.example                   环境变量模板（复制为 .env 后填写；.env 不提交）
docs/
  index.md                     学习网站首页与文档索引
  学习路线.md                  Python 学习路线：目标、11 个阶段、练习，链接到各阶段课程
  课程大纲.md                  课程定位、与官方教程对比、各阶段课时与目标
  课程/                        课程正文：NN-阶段/NN-课.md，每阶段含 index.md 导读；附录/ 含速查表、术语表
  Python概览与环境.md          Python 特点、版本现状、环境概念与 uv 用法
  代码解读/minimal_agent.md    minimal_agent.py 逐段语法解读
  项目架构与技术栈.md          目录职责、运行机制、技术栈版本与命令
  关于.md                      作者与联系、许可、声明、第三方组件
examples/
  agent/                       最小 Agent 循环示例（工具调用）
site/                          VitePress 学习网站（渲染 docs/；依赖只装在 site/node_modules）
tests/check_course.py          课程校验：执行全部示例与参考答案，检查结构与链接
```

## 快速开始

```bash
cp .env.example .env                      # 填写 DEEPSEEK_API_KEY
uv sync                                   # 按 uv.lock 创建 .venv 并安装依赖
uv run examples/agent/minimal_agent.py    # 运行最小 Agent 示例
```

学习网站：`cd site && npm install && npm run build && npm run preview`，打开 http://127.0.0.1:5180/（详见下文）。

## 文档索引

学习：

- [课程大纲](docs/课程大纲.md)：定位、与官方教程对比、各阶段课时与目标
- [学习路线](docs/学习路线.md)：从零到“能看懂代码”的阶段计划；每阶段链接到对应课程与官方延伸阅读
- [课程正文](docs/课程/)：`NN-阶段/NN-课.md`，每阶段含 `index.md` 导读
- [速查表](docs/课程/附录/速查表.md)、[术语表](docs/课程/附录/术语表.md)

参考：

- [Python 概览与环境](docs/Python概览与环境.md)：Python 是什么、版本现状、uv 环境
- [读懂 minimal_agent.py](docs/代码解读/minimal_agent.md)：示例代码逐段解读（课程中的逐行精读见 [11.1](docs/课程/11-简单项目/01-minimal_agent逐行精读.md)）
- [examples/agent](examples/agent/README.md)：最小 Agent 循环的原理、运行与验证结果

项目：

- [项目架构与技术栈](docs/项目架构与技术栈.md)：目录职责、构建与运行机制、技术栈版本、命令与设计决策
- [关于与声明](docs/关于.md)、[反馈与贡献](CONTRIBUTING.md)、[更新记录](CHANGELOG.md)

## 实验记录

| 实验 | 目的 | 依赖 | 状态（2026-10-06） | 说明 |
|---|---|---|---|---|
| 最小 Agent 循环 | 理解“模型决定 → 执行工具 → 回填结果”循环 | `anthropic`、`python-dotenv` | DeepSeek（`deepseek-flash`，Anthropic 兼容端点）已实测通过；Anthropic 官方 API 未实测 | [examples/agent](examples/agent/README.md) |

## Python 课程与学习网站（2026-10-06 新增）

面向有 JS/Java 经验开发者的中文 Python 课程：11 个阶段、36 课，每课含目标、核心概念、易错点、JS/Java 对照、读代码、自动判题练习、小结与延伸阅读，终点是逐行读懂 `examples/agent/minimal_agent.py`。课程 Markdown 位于 `docs/课程/`，是唯一内容来源；`site/` 是渲染它的 VitePress 网站。

### 启动网站

```bash
cd site
npm install            # 依赖仅安装在 site/node_modules
npm run build          # 构建（会先把 Pyodide 与示例源码复制到 site/public/）
npm run preview        # 前台预览：http://127.0.0.1:5180/
# 或后台常驻（nohup + setsid，关闭终端不退出）：
npm run serve:bg       # 停止：bash scripts/serve-bg.sh --stop
npm run dev            # 编写课程时用：修改 Markdown 实时刷新
```

网站功能：侧边栏与上一课/下一课导航、中文全文搜索、深色/浅色模式、学习进度（保存在本机浏览器 localStorage）、可编辑运行的代码块（Pyodide，即浏览器内的 Python 3.14，在 Web Worker 中执行，10 秒超时自动终止）、练习自动判题与参考答案。

Pyodide 已从 npm 包复制到本地（`site/public/pyodide/`，离线可用）；本地文件加载失败时自动改用 jsDelivr CDN（`cdn.jsdelivr.net/pyodide/v314.0.7/full/`）。

### 校验课程代码

```bash
uv run python tests/check_course.py          # 用项目的 Python（3.12）执行全部示例与参考答案，并检查结构与链接
python3 tests/check_course.py --python python3.12 --python python3.14   # 多版本
cd site && npm run verify:pyodide            # 用浏览器同版本的 Pyodide 执行全部代码块
cd site && npm run smoke                     # 浏览器冒烟测试（需本机 Chrome 且站点已启动）
```

### 课程文档索引

课程相关文档已并入上方 [文档索引](#文档索引)（学习部分）。

## 部署

- CI：`.github/workflows/ci.yml` 在推送与 PR 时运行课程校验、Pyodide 校验、站点构建与冒烟测试。
- GitHub Pages：`.github/workflows/pages.yml` 以 `SITE_BASE=/jdp-python/` 构建并发布，目标地址 `https://lixudong1649.github.io/jdp-python/`。需在仓库设置中启用 Pages（Source：GitHub Actions）；私有仓库需付费套餐，且发布后的站点默认公开可访问。

## 许可与声明

© 2026 [lixudong1649](https://github.com/lixudong1649)

| 范围 | 许可 |
|---|---|
| 代码：`examples/`、`site/`、`tests/`，以及 `docs/` 中的代码示例与练习 | [MIT](LICENSE) |
| 课程文字、表格与图示：`docs/` | [CC BY-NC-SA 4.0](LICENSE-CONTENT.md) |

本项目仅用于学习，与 Python Software Foundation、Anthropic、DeepSeek 无隶属关系；相关商标归各自所有者所有。第三方组件（Pyodide 等）遵循各自许可。内容可能有误，欢迎通过 [Issues](https://github.com/lixudong1649/jdp-python/issues) 反馈。完整声明见 [关于](docs/关于.md)。
