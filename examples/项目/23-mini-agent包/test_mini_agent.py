import pytest
from mini_agent import describe_tool, list_tools, run_tool
from mini_agent.runner import ToolError


def test_run_tool_echo() -> None:
    assert run_tool("echo", text="hi") == "hi"


def test_run_tool_unknown_raises() -> None:
    with pytest.raises(ToolError, match="未知工具"):
        run_tool("missing")


def test_run_tool_bad_kwargs_raises() -> None:
    with pytest.raises(ToolError):
        run_tool("add", a=1)


def test_list_and_describe_tools() -> None:
    names = list_tools()
    assert "echo" in names
    assert "add" in describe_tool("add")
