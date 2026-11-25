"""Quick sort example using the Lomuto partition scheme."""

from typing import Iterator

from algorithm_api import Step


def sort(values: list[int]) -> Iterator[Step]:
    data = values.copy()

    def quick_sort(start: int, end: int) -> Iterator[Step]:
        if start >= end:
            return

        pivot = data[end]
        boundary = start
        for index in range(start, end):
            yield Step(data.copy(), (index, end))
            if data[index] < pivot:
                if boundary != index:
                    data[boundary], data[index] = data[index], data[boundary]
                    yield Step(data.copy(), (boundary, index), writes=2)
                boundary += 1

        if boundary != end:
            data[boundary], data[end] = data[end], data[boundary]
            yield Step(data.copy(), (boundary, end), writes=2)

        yield from quick_sort(start, boundary - 1)
        yield from quick_sort(boundary + 1, end)

    yield from quick_sort(0, len(data) - 1)
    yield Step(data.copy(), finished=True)
