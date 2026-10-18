import timing


def test_retry_succeeds_eventually() -> None:
    calls = {"n": 0}

    @timing.retry(times=3, exc=ValueError)
    def flaky() -> str:
        calls["n"] += 1
        if calls["n"] < 3:
            raise ValueError("nope")
        return "ok"

    assert flaky() == "ok"
    assert calls["n"] == 3
