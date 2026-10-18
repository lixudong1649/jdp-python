from ring_buffer import RingBuffer


def test_ring_basic() -> None:
    buf = RingBuffer(3)
    buf.append("a")
    buf.append("b")
    assert len(buf) == 2
    assert buf[0] == "a"
    assert "b" in buf
    assert list(buf) == ["a", "b"]


def test_ring_overwrite() -> None:
    buf = RingBuffer(2)
    for x in ("a", "b", "c"):
        buf.append(x)
    assert list(buf) == ["b", "c"]
