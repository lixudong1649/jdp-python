import asyncio

import pytest
from async_agent import AgentError, AgentSession, run_batch, run_once, run_with_session


def test_run_once_echoes_prompt() -> None:
    assert asyncio.run(run_once("hi")) == "echo:hi"


def test_run_once_rejects_blank_prompt() -> None:
    with pytest.raises(AgentError, match="prompt"):
        asyncio.run(run_once("   "))


def test_run_batch_preserves_order() -> None:
    out = asyncio.run(run_batch(["a", "b"]))
    assert out == ["echo:a", "echo:b"]


def test_run_with_session_records_history() -> None:
    session = AgentSession()
    asyncio.run(run_with_session("ping", session))
    assert session.history == ["ping -> echo:ping"]
