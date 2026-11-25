"""Shared interface for sorting algorithms used by the visualizer."""

from dataclasses import dataclass


@dataclass
class Step:
    """One animation frame, including array slots written during the step."""

    values: list[int]
    active: tuple[int, ...] = ()
    finished: bool = False
    writes: int = 0
