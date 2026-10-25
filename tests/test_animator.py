import tkinter as tk
from typing import cast

import pytest
from PIL import Image

from picture_loom.weaver import animator


@pytest.mark.parametrize(
    ("start", "end", "expected"),
    [
        ((0, 0), (3, 0), [(0, 0), (1, 0), (2, 0), (3, 0)]),
        ((0, 0), (3, 3), [(0, 0), (1, 1), (2, 2), (3, 3)]),
        ((0, 0), (1, 3), [(0, 0), (0, 1), (1, 2), (1, 3)]),
        ((1, 3), (0, 0), [(1, 3), (1, 2), (0, 1), (0, 0)]),
        ((3, 0), (0, 3), [(3, 0), (2, 1), (1, 2), (0, 3)]),
        ((2, 2), (2, 2), [(2, 2)]),
    ],
)
def test_bresenham_pixels(start, end, expected):
    assert list(animator.bresenham_line(start, end)) == expected


def test_fixed_start_ties_and_circular_blacklist():
    reference = Image.new("L", (1, 1), 255)
    nails = [(0, 0)] * 24
    segments = list(animator.iter_lines(reference, nails, max_lines=4))
    assert segments == [(0, 11), (11, 0), (0, 11), (11, 0)]


def test_darkest_path_and_whitening_without_mutating_input():
    reference = Image.new("RGB", (5, 5), "white")
    for coordinate in range(5):
        reference.putpixel((coordinate, 0), (0, 0, 0))
        reference.putpixel((4, coordinate), (0, 0, 0))
    original = reference.tobytes()
    nails = [(0, 0), (4, 0), (4, 4), (0, 4)]
    assert list(
        animator.iter_lines(reference, nails, max_lines=2, blacklist_size=0)
    ) == [(0, 1), (1, 2)]
    assert reference.mode == "RGB"
    assert reference.tobytes() == original


@pytest.mark.parametrize("budget, expected", [(0, []), (1, [(0, 1)])])
def test_segment_budget(budget, expected):
    assert (
        list(
            animator.iter_lines(
                Image.new("L", (2, 1)),
                [(0, 0), (1, 0)],
                max_lines=budget,
                blacklist_size=0,
            )
        )
        == expected
    )


@pytest.mark.parametrize("nails", [[], [(0, 0)], [(0, 0)] * 21])
def test_no_eligible_candidates(nails):
    assert list(animator.iter_lines(Image.new("L", (1, 1)), nails)) == []


def test_scoring_uses_only_in_bounds_pixels():
    reference = Image.new("L", (3, 1), 100)
    reference.putpixel((1, 0), 0)
    assert list(
        animator.iter_lines(
            reference,
            [(0, 0), (1, 0), (4, 0)],
            max_lines=1,
            blacklist_size=0,
        )
    ) == [(0, 1)]


def test_paths_without_reference_pixels_are_not_candidates():
    assert (
        list(
            animator.iter_lines(
                Image.new("L", (1, 1)),
                [(2, 2), (3, 3)],
                max_lines=1,
                blacklist_size=0,
            )
        )
        == []
    )


def test_fast_mode_draws_generated_bresenham_segment():
    nails = [(0, 0)] * 11 + [(3, 0)] + [(3, 3)] * 12
    image = Image.new("RGB", (4, 4), "white")
    rendered = animator.fast_mode(image, Image.new("L", (4, 4), 0), nails, max_lines=1)
    assert rendered.getpixel((1, 0)) == (0, 0, 0, 255)
    assert rendered.getpixel((3, 3)) == (255, 255, 255, 255)


def test_gui_schedules_one_shared_segment_per_callback(monkeypatch):
    nails = [(0, 0)] * 11 + [(3, 0)] + [(3, 3)] * 12
    reference = Image.new("L", (4, 4), 0)
    expected = list(animator.iter_lines(reference, nails, max_lines=2))

    class Root:
        def __init__(self):
            self.callbacks = []
            self.delays = []

        def after(self, delay, callback):
            self.delays.append(delay)
            self.callbacks.append(callback)

    class Canvas:
        image = None

        def create_image(self, *args, **kwargs):
            self.image = kwargs["image"]
            return 1

        def itemconfig(self, image_id, **kwargs):
            self.image = kwargs["image"]

    root = Root()
    canvas = Canvas()
    monkeypatch.setattr(animator.ImageTk, "PhotoImage", lambda image: image)
    animator.run(
        cast(tk.Tk, root),
        cast(tk.Canvas, canvas),
        Image.new("RGB", (4, 4), "white"),
        reference,
        nails,
        max_lines=2,
        stroke_alpha=255,
    )
    assert root.delays == [100]
    root.callbacks.pop(0)()
    assert root.delays == [100, 20]
    root.callbacks.pop(0)()
    assert root.delays == [100, 20, 20]
    root.callbacks.pop(0)()
    assert root.delays == [100, 20, 20]
    expected_image = animator.fast_mode(
        Image.new("RGB", (4, 4), "white"), reference, nails, max_lines=len(expected)
    )
    assert cast(Image.Image, canvas.image).tobytes() == expected_image.tobytes()
