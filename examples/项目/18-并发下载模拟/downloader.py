"""模拟并发下载（线程池，阶段 18）。"""
from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field


class DownloadError(Exception):
    """下载失败（模拟 HTTP 错误或超时）。"""

    def __init__(self, url: str, reason: str) -> None:
        self.url = url
        self.reason = reason
        super().__init__(f"{url}: {reason}")


@dataclass
class FetchOutcome:
    url: str
    body: str | None = None
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None


@dataclass
class BatchResult:
    bodies: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def fetch(url: str, delay: float = 0.01, *, fail_if: str | None = None) -> str:
    if not url.strip():
        raise ValueError("url 不能为空")
    time.sleep(delay)
    if fail_if and fail_if in url:
        raise DownloadError(url, "simulated failure")
    return f"body:{url}"


def _safe_fetch(url: str, delay: float, fail_if: str | None) -> FetchOutcome:
    try:
        return FetchOutcome(url=url, body=fetch(url, delay, fail_if=fail_if))
    except DownloadError as e:
        return FetchOutcome(url=url, error=str(e))


def download_all(
    urls: list[str],
    *,
    workers: int = 4,
    delay: float = 0.01,
    fail_if: str | None = None,
    raise_on_error: bool = False,
) -> list[str]:
    if workers < 1:
        raise ValueError("workers 至少为 1")
    if not urls:
        return []
    result = BatchResult()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_safe_fetch, u, delay, fail_if): u for u in urls}
        for fut in as_completed(futures):
            outcome = fut.result()
            if outcome.ok and outcome.body is not None:
                result.bodies.append(outcome.body)
            elif outcome.error:
                result.errors.append(outcome.error)
    if raise_on_error and result.errors:
        raise DownloadError("batch", result.errors[0])
    return sorted(result.bodies)
