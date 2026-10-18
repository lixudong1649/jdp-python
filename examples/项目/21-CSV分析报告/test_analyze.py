from pathlib import Path

import pytest
from analyze import AnalyzeError, avg_column, column_stats, main


def test_avg_column() -> None:
    text = "city,temp\n上海,22\n北京,18\n"
    assert avg_column(text, "temp") == 20.0


def test_column_stats_includes_spread() -> None:
    text = "city,temp\n上海,22\n北京,18\n广州,26\n"
    stats = column_stats(text, "temp")
    assert stats["count"] == 3.0
    assert stats["min"] == 18.0
    assert stats["max"] == 26.0


def test_missing_column_raises() -> None:
    text = "city,temp\n上海,22\n"
    with pytest.raises(AnalyzeError, match="缺少列"):
        avg_column(text, "humidity")


def test_main_prints_report(tmp_path: Path) -> None:
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("city,temp\n上海,22\n北京,18\n", encoding="utf-8")
    assert main([str(csv_file), "temp"]) == 0
