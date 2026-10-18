from pathlib import Path

from logstats_pkg.cli import count_levels, main


def test_count_levels() -> None:
    assert dict(count_levels("INFO a\nERROR b\n")) == {"INFO": 1, "ERROR": 1}


def test_main(tmp_path: Path) -> None:
    p = tmp_path / "x.log"
    p.write_text("INFO x\n", encoding="utf-8")
    assert main(p) == 0
