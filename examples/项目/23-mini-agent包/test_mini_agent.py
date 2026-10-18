from mini_agent import run_tool


def test_run_tool() -> None:
    assert run_tool("echo", text="hi") == "hi"
