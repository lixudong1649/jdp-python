"""阶段 15：为 14 的 CLI 补 pytest 测试。"""
from pathlib import Path

from logstats import main, parse_lines


def test_main_on_sample(tmp_path: Path) -> None:
    log = tmp_path / "app.log"
    log.write_text("line INFO one\nline ERROR two\n", encoding="utf-8")
    assert main([str(log)]) == 0


def test_parse_empty() -> None:
    assert dict(parse_lines("")) == {}
