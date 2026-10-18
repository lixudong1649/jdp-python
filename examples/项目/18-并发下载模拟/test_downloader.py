import pytest
from downloader import DownloadError, download_all, fetch


def test_download_all_collects_sorted_bodies() -> None:
    urls = ["a", "b", "c"]
    assert download_all(urls, workers=2, delay=0) == ["body:a", "body:b", "body:c"]


def test_download_all_empty_returns_empty_list() -> None:
    assert download_all([], workers=2) == []


def test_fetch_rejects_blank_url() -> None:
    with pytest.raises(ValueError, match="url"):
        fetch("   ")


def test_download_all_skips_simulated_failures_by_default() -> None:
    urls = ["ok", "bad-host", "fine"]
    bodies = download_all(urls, workers=2, delay=0, fail_if="bad")
    assert bodies == ["body:fine", "body:ok"]


def test_download_all_raise_on_error() -> None:
    with pytest.raises(DownloadError):
        download_all(["x-bad"], delay=0, fail_if="bad", raise_on_error=True)
