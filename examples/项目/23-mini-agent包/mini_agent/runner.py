from __future__ import annotations

from mini_agent.tools import REGISTRY


def run_tool(name: str, **kwargs: object) -> object:
    if name not in REGISTRY:
        raise KeyError(name)
    return REGISTRY[name](**kwargs)
