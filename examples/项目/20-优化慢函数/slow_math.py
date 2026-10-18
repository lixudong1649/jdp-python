"""可优化与不可优化对比（阶段 20）。"""
from __future__ import annotations

import cProfile
import io
import pstats
import timeit
from collections.abc import Callable


def _validate_n(n: int) -> None:
    if n < 0:
        raise ValueError("n 不能为负数")


def sum_squares_slow(n: int) -> int:
    _validate_n(n)
    total = 0
    for i in range(n):
        total += i * i
    return total


def sum_squares_fast(n: int) -> int:
    _validate_n(n)
    # n*(n-1)*(2n-1)//6
    return n * (n - 1) * (2 * n - 1) // 6


def benchmark_pair(
    n: int,
    *,
    number: int = 100,
    repeat: int = 3,
) -> dict[str, float]:
    _validate_n(n)
    if number < 1 or repeat < 1:
        raise ValueError("number 与 repeat 至少为 1")
    slow = min(timeit.repeat(lambda: sum_squares_slow(n), number=number, repeat=repeat))
    fast = min(timeit.repeat(lambda: sum_squares_fast(n), number=number, repeat=repeat))
    return {"slow_sec": slow, "fast_sec": fast, "speedup": slow / fast if fast else float("inf")}


def profile_function(func: Callable[[int], int], n: int, *, top_n: int = 5) -> str:
    _validate_n(n)
    profiler = cProfile.Profile()
    profiler.enable()
    func(n)
    profiler.disable()
    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.strip_dirs().sort_stats("cumulative").print_stats(top_n)
    return stream.getvalue()
