from downloader import download_all


def test_download_all() -> None:
    urls = ["a", "b", "c"]
    assert download_all(urls, workers=2) == ["body:a", "body:b", "body:c"]
