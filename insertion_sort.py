"""Insertion sort example."""

from typing import Iterator

from algorithm_api import Step


def sort(values: list[int]) -> Iterator[Step]:
    data = values.copy()
    for index in range(1, len(data)):
        cursor = index
        while cursor > 0:
            yield Step(data.copy(), (cursor - 1, cursor))
            if data[cursor - 1] <= data[cursor]:
                break
            data[cursor - 1], data[cursor] = data[cursor], data[cursor - 1]
            yield Step(data.copy(), (cursor - 1, cursor), writes=2)
            cursor -= 1
    yield Step(data.copy(), finished=True)
