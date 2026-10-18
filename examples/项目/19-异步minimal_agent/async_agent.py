"""异步版 minimal_agent 骨架（模拟 HTTP 客户端，阶段 19）。"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field


class AgentError(ValueError):
    """业务层输入或调用错误。"""


@dataclass
class FakeResponse:
    text: str
    model: str = "fake-mini"


@dataclass
class AgentSession:
    history: list[str] = field(default_factory=list)

    def record(self, prompt: str, reply: str) -> None:
        self.history.append(f"{prompt} -> {reply}")


class FakeAsyncClient:
    def __init__(self, *, latency: float = 0.0) -> None:
        self.latency = latency

    async def complete(self, prompt: str) -> FakeResponse:
        if not prompt.strip():
            raise AgentError("prompt 不能为空")
        if self.latency > 0:
            await asyncio.sleep(self.latency)
        else:
            await asyncio.sleep(0)
        return FakeResponse(text=f"echo:{prompt}")


async def run_once(prompt: str, *, client: FakeAsyncClient | None = None) -> str:
    owned = client or FakeAsyncClient()
    resp = await owned.complete(prompt)
    return resp.text


async def run_batch(prompts: list[str], *, client: FakeAsyncClient | None = None) -> list[str]:
    if not prompts:
        return []
    owned = client or FakeAsyncClient()
    tasks = [owned.complete(p) for p in prompts]
    responses = await asyncio.gather(*tasks)
    return [r.text for r in responses]


async def run_with_session(prompt: str, session: AgentSession) -> str:
    reply = await run_once(prompt)
    session.record(prompt, reply)
    return reply
