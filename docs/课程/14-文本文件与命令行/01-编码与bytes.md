---
title: 14.1 编码与 bytes
---

# 14.1 编码与 bytes

> 前置：2.3 字符串 · 约 25 分钟 · 官方对应：[二进制数据](https://docs.python.org/zh-cn/3/library/stdtypes.html#binary-sequence-types-bytes-bytearray-memoryview)

## 目标

- 区分 str 与 bytes
- 会用 encode/decode 指定 UTF-8

## 核心概念

```python run
text = "上海"
b = text.encode("utf-8")
print(b, b.decode("utf-8"))
```

## 易错点

- 文本文件用 str，二进制用 bytes。
- 默认 UTF-8，但 Windows 历史编码可能不同。

## 对照

| 概念 | Python | JS | Java |
|---|---|---|---|
| 本节重点 | 见官方文档 | — | — |

## 读代码

HTTP/SDK 载荷常在 JSON（str）与 bytes 间转换；读 `content-type` 判断。

## 练习

```python exercise id=s14-l01-bytes
# --- starter ---
s = 'a'
# --- solution ---
s = 'a'
b = s.encode('utf-8')
# --- check ---
assert b == b'a'
```

## 小结

- bytes 是二进制序列
- str.encode 与 bytes.decode 成对

## 延伸阅读

- [Unicode HOWTO](https://docs.python.org/zh-cn/3/howto/unicode.html)
