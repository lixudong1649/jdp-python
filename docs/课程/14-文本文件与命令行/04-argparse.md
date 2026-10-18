---
title: 14.4 argparse
---

# 14.4 argparse

> 前置：3.2 函数 · 约 25 分钟 · 官方对应：[argparse](https://docs.python.org/zh-cn/3/library/argparse.html)

## 目标

- 定义位置参数与可选 flag
- 在 main 中 parse 并返回 exit code

## 核心概念

```python run
import argparse

p = argparse.ArgumentParser()
p.add_argument("name")
args = p.parse_args(["Ada"])
print(args.name)
```

## 易错点

- `parse_args()` 在无 argv 时会读 sys.argv。
- 子命令用 add_subparsers。

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 本节重点 | 见官方文档 | — | — |

## 读代码

CLI 工具入口通常是 `if __name__ == '__main__'` + argparse；先找 subcommand。

## 练习

```python exercise id=s14-l04-arg
# --- starter ---
import argparse

p = argparse.ArgumentParser()
p.add_argument('x')
# --- solution ---
import argparse

p = argparse.ArgumentParser()
p.add_argument('x')
args = p.parse_args(['3'])
# --- check ---
assert args.x == '3'
```

## 小结

- argparse 生成帮助信息
- 适合可安装脚本 CLI

## 延伸阅读

- [argparse 教程](https://docs.python.org/zh-cn/3/howto/argparse.html)
