"""计时与重试装饰器（阶段 13 项目）。"""
from __future__ import annotations

import functools
import time
from collections.abc import Callable
from typing import TypeVar

F = TypeVar("F", bound=Callable[..., object])


def timed(func: F) -> F:
    @functools.wraps(func)
    def wrapper(*args: object, **kwargs: object) -> object:
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            ms = (time.perf_counter() - start) * 1000
            print(f"{func.__name__} {ms:.2f} ms")

    return wrapper  # type: ignore[return-value]


def retry(*, times: int, exc: type[BaseException] = Exception) -> Callable[[F], F]:
    if times < 1:
        raise ValueError("times 至少为 1")

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> object:
            last: BaseException | None = None
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exc as e:
                    last = e
                    if attempt == times:
                        break
            assert last is not None
            raise last

        return wrapper  # type: ignore[return-value]

    return decorator
