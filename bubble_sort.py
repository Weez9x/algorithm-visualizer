"""Bubble sort example. Copy this file to add another algorithm."""

from typing import Iterator

from algorithm_api import Step


def sort(values: list[int]) -> Iterator[Step]:
    data = values.copy()
    for end in range(len(data) - 1, 0, -1):
        swapped = False
        for index in range(end):
            yield Step(data.copy(), (index, index + 1))
            if data[index] > data[index + 1]:
                data[index], data[index + 1] = data[index + 1], data[index]
                swapped = True
                yield Step(data.copy(), (index, index + 1), writes=2)
        if not swapped:
            break
    yield Step(data.copy(), finished=True)
