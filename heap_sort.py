"""Heap sort example using an in-place max heap."""

from typing import Iterator

from algorithm_api import Step


def sort(values: list[int]) -> Iterator[Step]:
    data = values.copy()

    def sift_down(root: int, end: int) -> Iterator[Step]:
        while (child := root * 2 + 1) <= end:
            larger = child
            if child + 1 <= end:
                yield Step(data.copy(), (child, child + 1))
                if data[child + 1] > data[child]:
                    larger = child + 1
            yield Step(data.copy(), (root, larger))
            if data[root] >= data[larger]:
                return
            data[root], data[larger] = data[larger], data[root]
            yield Step(data.copy(), (root, larger), writes=2)
            root = larger

    for root in range(len(data) // 2 - 1, -1, -1):
        yield from sift_down(root, len(data) - 1)

    for end in range(len(data) - 1, 0, -1):
        data[0], data[end] = data[end], data[0]
        yield Step(data.copy(), (0, end), writes=2)
        yield from sift_down(0, end - 1)

    yield Step(data.copy(), finished=True)
