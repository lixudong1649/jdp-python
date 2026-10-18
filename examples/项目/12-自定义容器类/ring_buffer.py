"""支持 len、索引、迭代与 in 的环形缓冲区（阶段 12 项目）。"""
from __future__ import annotations

from collections.abc import Iterator


class RingBuffer:
    def __init__(self, capacity: int) -> None:
        if capacity < 1:
            raise ValueError("capacity 至少为 1")
        self._cap = capacity
        self._data: list[object | None] = [None] * capacity
        self._start = 0
        self._size = 0

    def append(self, item: object) -> None:
        idx = (self._start + self._size) % self._cap
        if self._size < self._cap:
            self._data[idx] = item
            self._size += 1
        else:
            self._data[self._start] = item
            self._start = (self._start + 1) % self._cap

    def __len__(self) -> int:
        return self._size

    def __getitem__(self, index: int) -> object:
        if not isinstance(index, int):
            raise TypeError("索引必须是 int")
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError(index)
        return self._data[(self._start + index) % self._cap]

    def __contains__(self, item: object) -> bool:
        for i in range(self._size):
            if self[i] == item:
                return True
        return False

    def __iter__(self) -> Iterator[object]:
        for i in range(self._size):
            yield self[i]

    def __repr__(self) -> str:
        return f"RingBuffer({list(self)!r}, cap={self._cap})"
