import pytest
from slow_math import benchmark_pair, profile_function, sum_squares_fast, sum_squares_slow


def test_sum_squares_slow_and_fast_agree() -> None:
    for n in (0, 1, 10, 100):
        assert sum_squares_slow(n) == sum_squares_fast(n)


def test_sum_squares_rejects_negative_n() -> None:
    with pytest.raises(ValueError, match="负数"):
        sum_squares_slow(-1)


def test_benchmark_pair_reports_speedup() -> None:
    stats = benchmark_pair(50, number=5, repeat=2)
    assert stats["fast_sec"] <= stats["slow_sec"]
    assert stats["speedup"] >= 1.0


def test_profile_function_returns_text() -> None:
    report = profile_function(sum_squares_slow, 20, top_n=3)
    assert "function calls" in report
