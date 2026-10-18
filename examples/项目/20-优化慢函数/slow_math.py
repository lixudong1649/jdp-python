"""可优化与不可优化对比（阶段 20）。"""
from __future__ import annotations


def sum_squares_slow(n: int) -> int:
    total = 0
    for i in range(n):
        total += i * i
    return total


def sum_squares_fast(n: int) -> int:
    # n*(n-1)*(2n-1)//6
    return n * (n - 1) * (2 * n - 1) // 6
