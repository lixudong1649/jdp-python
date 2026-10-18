"""模拟并发下载（线程池，阶段 18）。"""
from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def fetch(url: str, delay: float = 0.01) -> str:
    time.sleep(delay)
    return f"body:{url}"


def download_all(urls: list[str], *, workers: int = 4) -> list[str]:
    out: list[str] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(fetch, u): u for u in urls}
        for fut in as_completed(futures):
            out.append(fut.result())
    return sorted(out)
