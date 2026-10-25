"""Animator for deterministic Bresenham-driven string art."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Iterator, Sequence

from PIL import Image, ImageDraw, ImageTk


def bresenham_line(
    start: tuple[int, int], end: tuple[int, int]
) -> Iterator[tuple[int, int]]:
    """Yield every integer pixel from start through end, inclusively."""
    x, y = start
    end_x, end_y = end
    dx = abs(end_x - x)
    sx = 1 if x < end_x else -1
    dy = -abs(end_y - y)
    sy = 1 if y < end_y else -1
    error = dx + dy

    while True:
        yield x, y
        if (x, y) == (end_x, end_y):
            break
        doubled_error = 2 * error
        if doubled_error >= dy:
            error += dy
            x += sx
        if doubled_error <= dx:
            error += dx
            y += sy


def iter_lines(
    ref_image: Image.Image,
    nails: Sequence[tuple[int, int]],
    *,
    max_lines: int = 5000,
    blacklist_size: int = 10,
) -> Iterator[tuple[int, int]]:
    """Yield darkest eligible peg pairs, whitening each selected path."""
    if not nails or max_lines <= 0:
        return

    reference = ref_image.convert("L")
    pixels = reference.load()
    width, height = reference.size
    nail_count = len(nails)
    current = 0

    for _ in range(max_lines):
        best_index: int | None = None
        best_score: float | None = None
        best_path: list[tuple[int, int]] = []

        for candidate in range(nail_count):
            distance = abs(candidate - current)
            if min(distance, nail_count - distance) <= blacklist_size:
                continue
            path = [
                point
                for point in bresenham_line(nails[current], nails[candidate])
                if 0 <= point[0] < width and 0 <= point[1] < height
            ]
            if not path:
                continue
            score = sum(pixels[point] for point in path) / len(path)
            if best_score is None or score < best_score:
                best_score = score
                best_index = candidate
                best_path = path

        if best_index is None:
            break

        for point in best_path:
            pixels[point] = 255
        yield current, best_index
        current = best_index


def _draw_segment(
    draw_layer: ImageDraw.ImageDraw,
    nails: Sequence[tuple[int, int]],
    start_index: int,
    end_index: int,
    stroke_alpha: int,
) -> None:
    draw_layer.line(
        (*nails[start_index], *nails[end_index]),
        fill=(0, 0, 0, stroke_alpha),
        width=1,
    )


def run(
    root: tk.Tk,
    canvas: tk.Canvas,
    base_image: Image.Image,
    ref_image: Image.Image,
    nails: Sequence[tuple[int, int]],
    *,
    max_lines: int = 5000,
    stroke_alpha: int = 60,
    delay_ms: int = 20,
) -> None:
    """Animate the shared deterministic line sequence on the canvas."""
    drawing_layer = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
    draw_layer = ImageDraw.Draw(drawing_layer, "RGBA")
    composite = base_image.convert("RGBA").copy()
    composite.alpha_composite(drawing_layer)
    backdrop = ImageTk.PhotoImage(composite)
    image_id = canvas.create_image(0, 0, anchor=tk.NW, image=backdrop)
    canvas.image = backdrop  # type: ignore[attr-defined]
    lines = iter_lines(ref_image, nails, max_lines=max_lines)

    def step() -> None:
        try:
            start_index, end_index = next(lines)
        except StopIteration:
            return
        _draw_segment(draw_layer, nails, start_index, end_index, stroke_alpha)
        updated = base_image.convert("RGBA").copy()
        updated.alpha_composite(drawing_layer)
        image = ImageTk.PhotoImage(updated)
        canvas.image = image  # type: ignore[attr-defined]
        canvas.itemconfig(image_id, image=image)
        root.after(delay_ms, step)

    root.after(100, step)


def fast_mode(
    base_image: Image.Image,
    ref_image: Image.Image,
    nails: Sequence[tuple[int, int]],
    *,
    max_lines: int = 5000,
    stroke_alpha: int = 255,
) -> Image.Image:
    """Render the shared deterministic line sequence without a GUI."""
    drawing_layer = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
    draw_layer = ImageDraw.Draw(drawing_layer, "RGBA")
    for start_index, end_index in iter_lines(ref_image, nails, max_lines=max_lines):
        _draw_segment(draw_layer, nails, start_index, end_index, stroke_alpha)

    composite = base_image.convert("RGBA").copy()
    composite.alpha_composite(drawing_layer)
    return composite
