from greeter import greet


def test_greet() -> None:
    assert greet("py") == "hello, py"


def test_greet_empty_name() -> None:
    assert greet("") == "hello, "


def test_greet_unicode() -> None:
    assert greet("世界") == "hello, 世界"
