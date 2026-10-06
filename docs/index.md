---
layout: home
title: Python 读码实战课
hero:
  name: Python 读码实战课
  text: 从零到读懂真实代码
  tagline: 面向开发者的系统化 Python 课程。示例在浏览器内直接运行，练习自动判题，终点是逐行读懂 minimal_agent.py。
  image:
    src: /logo.svg
    alt: Python
  actions:
    - theme: brand
      text: 开始学习
      link: /课程/01-环境与工具/01-运行Python代码
    - theme: alt
      text: 课程大纲
      link: /课程大纲
    - theme: alt
      text: 速查表
      link: /课程/附录/速查表
features:
  - icon: ▶️
    title: 浏览器内运行
    details: 每个示例都可编辑、运行、重置；Python 3.14（Pyodide）在 Web Worker 中执行，无需安装。
  - icon: ✅
    title: 自动判题练习
    details: 每课配练习，提交后用隐藏断言检查；可查看参考答案与检查代码。所有参考答案均经真实 CPython 验证。
  - icon: 🔍
    title: 读真实代码
    details: 每课都有“读代码”一节，并标出该知识点在 minimal_agent.py 中的位置，最后一阶段逐行精读。
  - icon: 🧭
    title: 为开发者设计
    details: 简洁、精确；每课附 JS / Java 对照与易错点；进度保存在本机浏览器。
---

<CourseRoadmap />

## 如何使用

1. 按阶段顺序学习；每课先读“目标”，运行“核心概念”中的示例，再完成“练习”。
2. 示例右上角“编辑”可修改代码，`⌘/Ctrl + Enter` 运行；练习点“提交检查”自动判题。
3. 本地实践用项目环境：`uv run python`（交互式）或 `uv run 文件.py`。
4. 学完一课点页面底部“标记本课已完成”，进度会显示在侧边栏与本页路线图。

## 文档索引

| 文档 | 用途 |
|---|---|
| [课程大纲](课程大纲.md) | 定位、与官方教程对比、各阶段课时与目标 |
| [学习路线](学习路线.md) | 11 个阶段的目标与达成标志，链接到各阶段课程与官方延伸阅读 |
| [Python 概览与环境](Python概览与环境.md) | Python 特点、版本现状、环境概念与 uv 用法 |
| [速查表](课程/附录/速查表.md) | 语法与常用写法速查 |
| [术语表](课程/附录/术语表.md) | 术语中英对照，指向讲解课程 |
| [读懂 minimal_agent.py](代码解读/minimal_agent.md) | 按语法分类的示例代码速查（逐行精读见 [11.1](课程/11-简单项目/01-minimal_agent逐行精读.md)） |
| [项目架构与技术栈](项目架构与技术栈.md) | 目录职责、构建与运行机制、技术栈版本、命令与设计决策 |
| [关于与声明](关于.md) | 作者与联系、版权与许可、免责声明、第三方组件 |

> 内容源为 `docs/` 下的 Markdown；核对日期 2026-10-06，适用 Python 3.12–3.14。
