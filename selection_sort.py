"""Selection sort example."""

from typing import Iterator

from algorithm_api import Step


def sort(values: list[int]) -> Iterator[Step]:
    data = values.copy()
    for start in range(len(data)):
        smallest = start
        for index in range(start + 1, len(data)):
            yield Step(data.copy(), (smallest, index))
            if data[index] < data[smallest]:
                smallest = index
        if smallest != start:
            data[start], data[smallest] = data[smallest], data[start]
            yield Step(data.copy(), (start, smallest), writes=2)
    yield Step(data.copy(), finished=True)
