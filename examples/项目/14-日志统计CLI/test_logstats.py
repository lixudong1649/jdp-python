from logstats import parse_lines


def test_parse_lines() -> None:
    text = "2026-01-01 INFO hello\n2026-01-01 ERROR boom\n2026-01-01 INFO again"
    c = parse_lines(text)
    assert c["INFO"] == 2
    assert c["ERROR"] == 1
