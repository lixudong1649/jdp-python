from __future__ import annotations

from collections.abc import Callable
from typing import Any

ToolFn = Callable[..., Any]

REGISTRY: dict[str, ToolFn] = {}


def tool(name: str) -> Callable[[ToolFn], ToolFn]:
    if not name.strip():
        raise ValueError("工具名不能为空")

    def deco(fn: ToolFn) -> ToolFn:
        REGISTRY[name] = fn
        return fn

    return deco


def list_tools() -> list[str]:
    return sorted(REGISTRY.keys())


@tool("echo")
def echo(text: str) -> str:
    return text


@tool("length")
def length(text: str) -> int:
    return len(text)


@tool("add")
def add(a: int, b: int) -> int:
    return a + b
