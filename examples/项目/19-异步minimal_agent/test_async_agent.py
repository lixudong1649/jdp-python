import asyncio

from async_agent import run_once


def test_run_once() -> None:
    assert asyncio.run(run_once("hi")) == "echo:hi"
