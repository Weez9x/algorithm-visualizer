"""Interactive sorting visualizer built with Pygame."""

from __future__ import annotations

import random
import importlib.util
from pathlib import Path
import sys
from typing import Callable, Iterator

import pygame
from algorithm_api import Step


WIDTH, HEIGHT = 1100, 720
FPS = 60
BACKGROUND = (15, 19, 31)
PANEL = (24, 30, 46)
PANEL_LIGHT = (34, 42, 61)
TEXT = (232, 238, 248)
MUTED = (145, 158, 180)
ACCENT = (111, 133, 255)
CYAN = (59, 213, 198)
ORANGE = (255, 177, 92)
GREEN = (107, 220, 145)


def discover_algorithms() -> dict[str, Callable[[list[int]], Iterator[Step]]]:
    algorithms = {}
    for path in sorted(Path(__file__).parent.glob("*_sort.py")):
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        sys.modules[path.stem] = module
        spec.loader.exec_module(module)
        sorter = getattr(module, "sort", None)
        if callable(sorter):
            algorithms[path.name] = sorter
    return algorithms


class Button:
    def __init__(self, rect: pygame.Rect, label: str, callback, *, active=False):
        self.rect = rect
        self.label = label
        self.callback = callback
        self.active = active

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, mouse_pos) -> None:
        hovered = self.rect.collidepoint(mouse_pos)
        color = ACCENT if self.active else PANEL_LIGHT
        if hovered and not self.active:
            color = (48, 59, 82)
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        label = font.render(self.label, True, TEXT)
        surface.blit(label, label.get_rect(center=self.rect.center))


class Visualizer:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Sort Lab — визуализатор алгоритмов")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("dejavusans", 17)
        self.small = pygame.font.SysFont("dejavusans", 14)
        self.title_font = pygame.font.SysFont("dejavusans", 30, bold=True)
        self.algorithms = discover_algorithms()
        if not self.algorithms:
            raise RuntimeError("Не найдены алгоритмы: добавьте файл *_sort.py с функцией sort(values).")
        self.values: list[int] = []
        self.algorithm = next(iter(self.algorithms))
        self.array_size = 50
        self.speed = 4
        self.running = False
        self.complete = False
        self.generator: Iterator[Step] | None = None
        self.current = Step([])
        self.elapsed = 0.0
        self.comparisons = 0
        self.moves = 0
        self.algorithm_offset = 0
        self.dragging_slider: str | None = None
        self._make_buttons()
        self.new_array()

    def _make_buttons(self) -> None:
        self.algorithm_buttons = []
        self.algorithm_list_rows = min(3, len(self.algorithms))
        filenames = list(self.algorithms)
        max_offset = max(0, len(filenames) - self.algorithm_list_rows)
        self.algorithm_offset = min(self.algorithm_offset, max_offset)
        for row in range(self.algorithm_list_rows):
            name = filenames[self.algorithm_offset + row]
            y = 172 + row * 39
            button = Button(pygame.Rect(34, y, 320, 34), name,
                            lambda name=name: self.set_algorithm(name))
            self.algorithm_buttons.append(button)

        self.controls_y = 172 + self.algorithm_list_rows * 39 + 16
        self.panel_height = self.controls_y + 112
        self.chart_y = self.panel_height + 20
        self.buttons = [
            Button(pygame.Rect(34, self.controls_y + 48, 156, 42), "Новый массив", self.new_array),
            Button(pygame.Rect(202, self.controls_y + 48, 156, 42), "▶  Старт", self.start),
        ]

    def set_algorithm(self, name: str) -> None:
        self.algorithm = name
        self.reset_run()

    def set_array_size(self, value: int) -> None:
        value = max(10, min(100, value))
        if value != self.array_size:
            self.array_size = value
            self.new_array()

    def reset_run(self) -> None:
        self.running = False
        self.complete = False
        self.generator = None
        self.elapsed = 0.0
        self.comparisons = 0
        self.moves = 0
        self.current = Step(self.values.copy())

    def new_array(self) -> None:
        self.values = random.sample(range(10, 1001), self.array_size)
        self.reset_run()

    def start(self) -> None:
        if self.complete:
            self.new_array()
        if self.generator is None:
            self.generator = self.algorithms[self.algorithm](self.values)
        self.running = not self.running

    def advance(self) -> None:
        if not self.generator:
            return
        try:
            step = next(self.generator)
        except StopIteration:
            self.running = False
            self.complete = True
            return
        if step.active and step.writes == 0:
            self.comparisons += 1
        self.moves += step.writes
        self.values = step.values
        self.current = step
        if step.finished:
            self.running = False
            self.complete = True

    def _text(self, text: str, position: tuple[int, int], color=TEXT, font=None) -> None:
        self.screen.blit((font or self.font).render(text, True, color), position)

    def draw(self) -> None:
        width, height = self.screen.get_size()
        self.screen.fill(BACKGROUND)
        pygame.draw.rect(self.screen, PANEL, (20, 20, width - 40, self.panel_height), border_radius=18)
        self._text("SORT LAB", (36, 34), CYAN, self.small)
        self._text("Визуализатор алгоритмов", (34, 56), TEXT, self.title_font)
        self._text("Сравнивай алгоритмы сортировки в реальном времени", (36, 103), MUTED)
        self._text("ФАЙЛЫ АЛГОРИТМОВ", (36, 145), MUTED, self.small)
        if len(self.algorithms) > self.algorithm_list_rows:
            self._text("Колесо мыши — прокрутка", (196, 145), MUTED, self.small)
        for button in self.algorithm_buttons:
            button.active = button.label == self.algorithm
            button.draw(self.screen, self.font, pygame.mouse.get_pos())
        self._text("РАЗМЕР МАССИВА", (36, self.controls_y - 22), MUTED, self.small)
        for button in self.buttons:
            if button.callback == self.start:
                button.label = "Ⅱ  Пауза" if self.running else ("↻  Ещё раз" if self.complete else "▶  Старт")
            button.draw(self.screen, self.font, pygame.mouse.get_pos())
        size_x, slider_y, size_w = 34, self.controls_y + 20, max(170, min(420, width - 650))
        size_knob_x = size_x + int((self.array_size - 10) / 90 * size_w)
        pygame.draw.line(self.screen, PANEL_LIGHT, (size_x, slider_y), (size_x + size_w, slider_y), 6)
        pygame.draw.line(self.screen, ACCENT, (size_x, slider_y), (size_knob_x, slider_y), 6)
        pygame.draw.circle(self.screen, TEXT, (size_knob_x, slider_y), 10)
        for value in range(10, 101, 10):
            tick_x = size_x + int((value - 10) / 90 * size_w)
            pygame.draw.line(self.screen, MUTED, (tick_x, slider_y - 8), (tick_x, slider_y + 8), 2)
            tick_label = self.small.render(str(value), True, MUTED)
            self.screen.blit(tick_label, tick_label.get_rect(center=(tick_x, slider_y + 20)))
        self._text(f"{self.array_size}", (size_x + size_w + 16, slider_y - 10), TEXT)

        speed_x, speed_y, speed_w = 520, slider_y, max(170, width - 570)
        self._text("СКОРОСТЬ", (speed_x, self.controls_y - 22), MUTED, self.small)
        pygame.draw.line(self.screen, PANEL_LIGHT, (speed_x, speed_y), (speed_x + speed_w, speed_y), 6)
        speed_knob_x = speed_x + int((self.speed - 1) / 9 * speed_w)
        pygame.draw.line(self.screen, ACCENT, (speed_x, speed_y), (speed_knob_x, speed_y), 6)
        pygame.draw.circle(self.screen, TEXT, (speed_knob_x, speed_y), 10)
        self._text(f"{self.speed}×", (speed_x, speed_y + 20), MUTED, self.small)

        chart = pygame.Rect(20, self.chart_y, width - 40, height - self.chart_y - 24)
        pygame.draw.rect(self.screen, PANEL, chart, border_radius=18)
        elapsed = self.elapsed
        status = "Готово" if self.complete else ("Сортируем…" if self.running else "Готов к запуску")
        self._text(status, (42, chart.y + 18), GREEN if self.complete else CYAN)
        self._text(f"Сравнения  {self.comparisons:,}     Перемещения  {self.moves:,}     Время  {elapsed:.1f} с", (42, chart.y + 48), MUTED, self.small)
        self._draw_bars(chart)
        pygame.display.flip()

    def _draw_bars(self, chart: pygame.Rect) -> None:
        if not self.values:
            return
        pad_x, pad_y = 28, 24
        area = pygame.Rect(chart.x + pad_x, chart.y + 78, chart.width - pad_x * 2, chart.height - 102)
        gap = max(1, min(5, area.width // (len(self.values) * 4)))
        bar_w = max(1, (area.width - gap * (len(self.values) - 1)) / len(self.values))
        max_value = max(self.values)
        active = set(self.current.active)
        for index, value in enumerate(self.values):
            bar_h = max(3, int((value / max_value) * area.height))
            x = int(area.x + index * (bar_w + gap))
            y = area.bottom - bar_h
            color = ORANGE if index in active else (GREEN if self.complete else ACCENT)
            pygame.draw.rect(self.screen, color, (x, y, max(1, int(bar_w)), bar_h), border_radius=3)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
            pygame.quit()
            raise SystemExit
        if event.type == pygame.VIDEORESIZE:
            self.screen = pygame.display.get_surface()
            self._make_buttons()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in [*self.algorithm_buttons, *self.buttons]:
                if button.rect.collidepoint(event.pos):
                    button.callback()
                    break
            x, y = event.pos
            size_x, slider_y = 34, self.controls_y + 20
            size_w = max(170, min(420, self.screen.get_width() - 650))
            speed_x, speed_w = 520, max(170, self.screen.get_width() - 570)
            if size_x <= x <= size_x + size_w and abs(y - slider_y) <= 18:
                self.dragging_slider = "size"
                self._update_slider(x)
            elif speed_x <= x <= speed_x + speed_w and abs(y - slider_y) <= 18:
                self.dragging_slider = "speed"
                self._update_slider(x)
        if event.type == pygame.MOUSEMOTION and self.dragging_slider:
            if getattr(event, "buttons", (0, 0, 0))[0]:
                self._update_slider(event.pos[0])
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging_slider = None
        if event.type == pygame.MOUSEWHEEL and len(self.algorithms) > self.algorithm_list_rows:
            list_rect = pygame.Rect(34, 172, 320, self.algorithm_list_rows * 39)
            if list_rect.collidepoint(pygame.mouse.get_pos()):
                max_offset = len(self.algorithms) - self.algorithm_list_rows
                self.algorithm_offset = max(0, min(max_offset, self.algorithm_offset - event.y))
                self._make_buttons()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.start()
            elif event.key == pygame.K_r:
                self.new_array()

    def _update_slider(self, x: int) -> None:
        size_x = 34
        size_w = max(170, min(420, self.screen.get_width() - 650))
        speed_x = 520
        speed_w = max(170, self.screen.get_width() - 570)
        if self.dragging_slider == "size":
            progress = max(0.0, min(1.0, (x - size_x) / size_w))
            self.set_array_size(10 + round(progress * 90))
        elif self.dragging_slider == "speed":
            progress = max(0.0, min(1.0, (x - speed_x) / speed_w))
            self.speed = 1 + round(progress * 9)

    def run(self) -> None:
        while True:
            dt = self.clock.tick(FPS) / 1000
            for event in pygame.event.get():
                self.handle_event(event)
            if self.running:
                self.elapsed += dt
                self._step_accumulator = getattr(self, "_step_accumulator", 0) + dt
                interval = 0.22 / self.speed
                if self._step_accumulator >= interval:
                    self._step_accumulator %= interval
                    self.advance()
            else:
                self._step_accumulator = 0
            self.draw()


if __name__ == "__main__":
    Visualizer().run()
