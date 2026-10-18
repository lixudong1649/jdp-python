from __future__ import annotations

from collections.abc import Callable
from typing import Any

ToolFn = Callable[..., Any]

REGISTRY: dict[str, ToolFn] = {}


def tool(name: str) -> Callable[[ToolFn], ToolFn]:
    def deco(fn: ToolFn) -> ToolFn:
        REGISTRY[name] = fn
        return fn

    return deco


@tool("echo")
def echo(text: str) -> str:
    return text
