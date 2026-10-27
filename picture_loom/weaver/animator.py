"""Animator for deterministic Bresenham-driven string art."""

import random
import tkinter as tk
from collections.abc import Callable, Iterator, Sequence

from PIL import Image, ImageTk


def bresenham_line(
    start: tuple[int, int], end: tuple[int, int]
) -> Iterator[tuple[int, int]]:
    """Yield every integer pixel from start through end, inclusively."""
    x, y = start
    end_x, end_y = end
    dx = abs(end_x - x)
    dy = abs(end_y - y)
    sx = 1 if x < end_x else -1 if x > end_x else 0
    sy = 1 if y < end_y else -1 if y > end_y else 0
    error = dx - dy

    while True:
        yield x, y
        if (x, y) == (end_x, end_y):
            break
        doubled_error = 2 * error
        if doubled_error > -dy:
            error -= dy
            x += sx
        if doubled_error < dx:
            error += dx
            y += sy


def iter_lines(
    ref_image: Image.Image,
    nails: Sequence[tuple[int, int]],
    *,
    max_lines: int = 5000,
    blacklist_size: int = 10,
    candidate_count: int = 30,
    stroke_alpha: int = 255,
) -> Iterator[tuple[int, int]]:
    """Yield seeded sampled peg pairs while compositing white over each path.

    Args:
        ref_image: Grayscale scoring image; the input is not mutated.
        nails: Peg coordinates in circular order.
        max_lines: Maximum number of segments to yield.
        blacklist_size: Number of neighboring pegs excluded on either side.
        candidate_count: Number of eligible endpoints sampled per segment.
        stroke_alpha: Opacity of white residual strokes, from 0 through 255.

    Yields:
        Start and end peg indexes for each selected segment.
    """
    if not nails or max_lines <= 0 or candidate_count <= 0:
        return

    reference = ref_image.convert("L" if ref_image.mode == "L" else "RGB")
    pixels = reference.load()
    width, height = reference.size
    nail_count = len(nails)
    sampler = random.Random(0)
    current = sampler.randrange(nail_count)

    for _ in range(max_lines):
        eligible = [
            candidate
            for candidate in range(nail_count)
            if min(
                abs(candidate - current),
                nail_count - abs(candidate - current),
            )
            > blacklist_size
        ]
        sampled = sampler.sample(eligible, min(candidate_count, len(eligible)))
        best_index: int | None = None
        best_score: float | None = None
        best_path: list[tuple[int, int]] = []

        for candidate in sampled:
            path = [
                point
                for point in bresenham_line(nails[current], nails[candidate])
                if 0 <= point[0] < width and 0 <= point[1] < height
            ]
            if not path:
                continue
            if reference.mode == "L":
                score = sum(pixels[point] for point in path) / len(path)
            else:
                score = sum(
                    sum(pixels[point]) / 3 for point in path
                ) / len(path)
            if best_score is None or score <= best_score:
                best_score = score
                best_index = candidate
                best_path = path

        if best_index is None:
            break

        for point in best_path:
            old = pixels[point]
            if reference.mode == "L":
                pixels[point] = round(
                    old * (255 - stroke_alpha) / 255 + stroke_alpha
                )
            else:
                pixels[point] = tuple(
                    round(channel * (255 - stroke_alpha) / 255 + stroke_alpha)
                    for channel in old
                )
        yield current, best_index
        current = best_index


def _draw_segment(
    composite: Image.Image,
    nails: Sequence[tuple[int, int]],
    start_index: int,
    end_index: int,
    stroke_alpha: int,
) -> None:
    """Composite one semi-transparent black segment into the board.

    Args:
        composite: RGBA board updated in place.
        nails: Peg coordinates indexed by the segment endpoints.
        start_index: Index of the first endpoint peg.
        end_index: Index of the second endpoint peg.
        stroke_alpha: Black stroke opacity from 0 through 255.
    """
    if stroke_alpha <= 0:
        return

    pixels = composite.load()
    width, height = composite.size
    for x, y in bresenham_line(nails[start_index], nails[end_index]):
        if not (0 <= x < width and 0 <= y < height):
            continue
        red, green, blue, old_alpha = pixels[x, y]
        out_alpha = stroke_alpha + round(old_alpha * (255 - stroke_alpha) / 255)
        if out_alpha:
            scale = old_alpha * (255 - stroke_alpha) / (255 * out_alpha)
            pixels[x, y] = (
                round(red * scale),
                round(green * scale),
                round(blue * scale),
                out_alpha,
            )
        else:
            pixels[x, y] = (0, 0, 0, 0)


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
    """Animate shared deterministic segments on the Tk canvas.

    Args:
        root: Tk root used to schedule animation frames.
        canvas: Canvas displaying the composed board.
        base_image: Board image before string segments are drawn.
        ref_image: Grayscale image used to score candidate segments.
        nails: Peg coordinates in circular order.
        max_lines: Maximum number of segments to draw.
        stroke_alpha: Black string opacity from 0 through 255.
        delay_ms: Delay between rendered segments in milliseconds.
    """
    composite = base_image.convert("RGBA").copy()
    backdrop = ImageTk.PhotoImage(composite)
    image_id = canvas.create_image(0, 0, anchor=tk.NW, image=backdrop)
    canvas.image = backdrop  # type: ignore[attr-defined]
    lines = iter_lines(
        ref_image, nails, max_lines=max_lines, stroke_alpha=stroke_alpha
    )

    def step() -> None:
        """Draw the next line and schedule another animation frame."""
        try:
            start_index, end_index = next(lines)
        except StopIteration:
            return
        _draw_segment(composite, nails, start_index, end_index, stroke_alpha)
        image = ImageTk.PhotoImage(composite)
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
    progress_callback: Callable[[int, Image.Image], None] | None = None,
) -> Image.Image:
    """Render segments headlessly, reporting independent progress snapshots.

    Args:
        base_image: Board image before string segments are drawn.
        ref_image: Grayscale image used to score candidate segments.
        nails: Peg coordinates in circular order.
        max_lines: Maximum number of segments to draw.
        stroke_alpha: Opacity of black string segments, from 0 through 255.
        progress_callback: Optional callback receiving percentage and snapshot.

    Returns:
        The final composed board image.
    """
    composite = base_image.convert("RGBA").copy()
    thresholds = {
        (percentage * max_lines + 99) // 100: percentage
        for percentage in (20, 40, 60, 80)
    }
    completed = 0
    for start_index, end_index in iter_lines(
        ref_image,
        nails,
        max_lines=max_lines,
        stroke_alpha=stroke_alpha,
    ):
        _draw_segment(composite, nails, start_index, end_index, stroke_alpha)
        completed += 1
        percentage = thresholds.get(completed)
        if progress_callback is not None and percentage is not None:
            progress_callback(percentage, composite.copy())

    return composite
