"""Merge sort example."""

from typing import Iterator

from algorithm_api import Step


def sort(values: list[int]) -> Iterator[Step]:
    data = values.copy()

    def merge_sort(start: int, end: int) -> Iterator[Step]:
        if end - start < 2:
            return
        middle = (start + end) // 2
        yield from merge_sort(start, middle)
        yield from merge_sort(middle, end)

        left = data[start:middle]
        right = data[middle:end]
        left_index = right_index = 0
        output_index = start
        while left_index < len(left) and right_index < len(right):
            yield Step(data.copy(), (start + left_index, middle + right_index))
            if left[left_index] <= right[right_index]:
                data[output_index] = left[left_index]
                left_index += 1
            else:
                data[output_index] = right[right_index]
                right_index += 1
            yield Step(data.copy(), (output_index,), writes=1)
            output_index += 1

        while left_index < len(left):
            data[output_index] = left[left_index]
            yield Step(data.copy(), (output_index,), writes=1)
            left_index += 1
            output_index += 1

        while right_index < len(right):
            data[output_index] = right[right_index]
            yield Step(data.copy(), (output_index,), writes=1)
            right_index += 1
            output_index += 1

    yield from merge_sort(0, len(data))
    yield Step(data.copy(), finished=True)
