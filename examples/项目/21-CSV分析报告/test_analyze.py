from analyze import avg_column


def test_avg_column() -> None:
    text = "city,temp\n上海,22\n北京,18\n"
    assert avg_column(text, "temp") == 20.0
