from slow_math import sum_squares_fast, sum_squares_slow


def test_equivalent() -> None:
    for n in (0, 1, 10, 100):
        assert sum_squares_slow(n) == sum_squares_fast(n)
