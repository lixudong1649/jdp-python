from __future__ import annotations

import inspect
from typing import Any

from mini_agent.tools import REGISTRY


class ToolError(KeyError):
    """调用未知工具或参数不匹配。"""


def _bind_kwargs(fn: Any, kwargs: dict[str, object]) -> dict[str, object]:
    sig = inspect.signature(fn)
    try:
        bound = sig.bind(**kwargs)
    except TypeError as e:
        raise ToolError(str(e)) from e
    bound.apply_defaults()
    return dict(bound.arguments)


def run_tool(name: str, **kwargs: object) -> object:
    if name not in REGISTRY:
        raise ToolError(f"未知工具: {name}")
    fn = REGISTRY[name]
    try:
        bound = _bind_kwargs(fn, kwargs)
    except ToolError:
        raise
    return fn(**bound)


def describe_tool(name: str) -> str:
    if name not in REGISTRY:
        raise ToolError(f"未知工具: {name}")
    fn = REGISTRY[name]
    sig = inspect.signature(fn)
    return f"{name}{sig}"
