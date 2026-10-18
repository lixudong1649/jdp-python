"""异步版 minimal_agent 骨架（模拟 HTTP 客户端，阶段 19）。"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass


@dataclass
class FakeResponse:
    text: str


class FakeAsyncClient:
    async def complete(self, prompt: str) -> FakeResponse:
        await asyncio.sleep(0)
        return FakeResponse(text=f"echo:{prompt}")


async def run_once(prompt: str) -> str:
    client = FakeAsyncClient()
    resp = await client.complete(prompt)
    return resp.text
