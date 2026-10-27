import tkinter as tk
from typing import cast

import pytest
from PIL import Image

from picture_loom.weaver import animator
from picture_loom.weaver.loom import calculate_pegs


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


def test_seeded_start_and_sample_order_break_ties():
    reference = Image.new("L", (2, 1), 0)
    reference.putpixel((1, 0), 255)
    nails = [(0, 0)] * 24
    nails[23] = (1, 0)
    assert list(animator.iter_lines(reference, nails, max_lines=1)) == [(12, 0)]


def test_rgb_scoring_uses_arithmetic_channel_mean():
    reference = Image.new("RGB", (3, 2), "white")
    reference.putpixel((0, 0), (255, 0, 0))
    reference.putpixel((1, 1), (0, 180, 0))
    original = reference.tobytes()
    nails = [(0, 1)] * 24
    nails[1] = (0, 0)
    nails[0] = (1, 1)
    assert list(animator.iter_lines(reference, nails, max_lines=1)) == [(12, 0)]
    assert reference.tobytes() == original


def test_reference_bresenham_strict_tie_steps():
    assert list(animator.bresenham_line((0, 0), (1, 2))) == [
        (0, 0), (0, 1), (1, 2)
    ]


def test_alpha_38_residual_keeps_a_darker_return_path():
    reference = Image.new("L", (4, 1), 200)
    reference.putpixel((0, 0), 0)
    reference.putpixel((1, 0), 0)
    reference.putpixel((2, 0), 42)
    nails = [(3, 0)] * 24
    nails[1] = (1, 0)
    nails[12] = (0, 0)
    nails[14] = (2, 0)
    assert list(
        animator.iter_lines(reference, nails, max_lines=2, stroke_alpha=38)
    ) == [(12, 1), (1, 12)]
    assert list(
        animator.iter_lines(reference, nails, max_lines=2, stroke_alpha=255)
    ) == [(12, 1), (1, 14)]


@pytest.mark.parametrize("mirrored", [False, True])
def test_greedy_path_follows_mirrored_off_center_dark_feature(mirrored):
    reference = Image.new("RGB", (5, 5), "white")
    feature_x = 4 if mirrored else 0
    reference.putpixel((feature_x, 2), (0, 0, 0))
    nails = [(2, 2)] * 24
    nails[0] = (4 if mirrored else 0, 2)
    nails[1] = (2, 0)
    original = reference.tobytes()
    assert list(animator.iter_lines(reference, nails, max_lines=1)) == [(12, 0)]
    assert reference.tobytes() == original


def test_fixed_start_ties_and_circular_blacklist():
    reference = Image.new("L", (1, 1), 255)
    nails = [(0, 0)] * 24
    segments = list(animator.iter_lines(reference, nails, max_lines=4))
    assert segments == [(12, 23), (23, 10), (10, 21), (21, 9)]


def test_darkest_path_and_whitening_without_mutating_input():
    reference = Image.new("RGB", (5, 5), "white")
    for coordinate in range(5):
        reference.putpixel((coordinate, 0), (0, 0, 0))
        reference.putpixel((4, coordinate), (0, 0, 0))
    original = reference.tobytes()
    nails = [(0, 0), (4, 0), (4, 4), (0, 4)]
    assert list(
        animator.iter_lines(reference, nails, max_lines=2, blacklist_size=0)
    ) == [(3, 2), (2, 1)]
    assert reference.mode == "RGB"
    assert reference.tobytes() == original


@pytest.mark.parametrize("budget, expected", [(0, []), (1, [(1, 0)])])
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
    ) == [(1, 0)]


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
    nails = [(0, 0)] * 24
    nails[23] = (3, 0)
    image = Image.new("RGB", (4, 4), "white")
    rendered = animator.fast_mode(
        image, Image.new("L", (4, 4), 0), nails, max_lines=1
    )
    assert rendered.getpixel((1, 0)) == (0, 0, 0, 255)
    assert rendered.getpixel((3, 3)) == (255, 255, 255, 255)


def test_gui_schedules_one_shared_segment_per_callback(monkeypatch):
    nails = [(0, 0)] * 24
    nails[23] = (3, 0)
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


def test_seeded_sampling_can_skip_the_exhaustive_darkest_path():
    reference = Image.new("L", (65, 1), 255)
    reference.putpixel((11, 0), 0)
    nails = [(x, 0) for x in range(65)]
    assert list(animator.iter_lines(reference, nails, max_lines=1)) == [(49, 10)]
    assert list(animator.iter_lines(reference, nails, max_lines=1)) == [(49, 10)]
    assert list(
        animator.iter_lines(reference, nails, max_lines=1, candidate_count=65)
    ) == [(49, 11)]


def test_single_candidate_sampling_uses_a_local_seed():
    reference = Image.new("L", (3, 1), 0)
    reference.putpixel((2, 0), 100)
    assert list(
        animator.iter_lines(
            reference,
            [(0, 0), (1, 0), (2, 0)],
            max_lines=1,
            blacklist_size=0,
            candidate_count=1,
        )
    ) == [(1, 2)]


@pytest.mark.parametrize(
    ("alpha", "expected"),
    [
        (0, [(1, 0), (0, 1)]),
        (38, [(1, 0), (0, 1)]),
        (60, [(1, 0), (0, 1)]),
        (128, [(1, 0), (0, 2)]),
        (255, [(1, 0), (0, 2)]),
    ],
)
def test_residual_opacity_changes_subsequent_scoring(alpha, expected):
    reference = Image.new("L", (5, 1), 0)
    reference.putpixel((3, 0), 100)
    reference.putpixel((4, 0), 100)
    assert list(
        animator.iter_lines(
            reference,
            [(0, 0), (2, 0), (4, 0)],
            max_lines=2,
            blacklist_size=0,
            stroke_alpha=alpha,
        )
    ) == expected
    assert [reference.getpixel((x, 0)) for x in range(5)] == [0, 0, 0, 100, 100]


def test_fast_mode_progress_snapshots_cross_budget_thresholds():
    nails = [(32 + x, 32 + y) for x, y in calculate_pegs(30, 32)]
    image = Image.new("RGB", (64, 64), "white")
    checkpoints = []
    result = animator.fast_mode(
        image,
        Image.new("L", image.size, 0),
        nails,
        max_lines=5,
        progress_callback=lambda percentage, snapshot: checkpoints.append(
            (percentage, snapshot)
        ),
    )
    assert [percentage for percentage, _ in checkpoints] == [20, 40, 60, 80]
    drawn_pixels = [
        sum(
            snapshot.getpixel((x, y)) != (255, 255, 255, 255)
            for x in range(64)
            for y in range(64)
        )
        for _, snapshot in checkpoints
    ]
    assert drawn_pixels == [52, 103, 148, 200]
    assert all(
        checkpoints[index - 1][1].tobytes() != checkpoints[index][1].tobytes()
        for index in range(1, len(checkpoints))
    )
    assert checkpoints[0][1] is not checkpoints[1][1]
    assert checkpoints[0][1].tobytes() != result.tobytes()
    assert checkpoints[0][1].getpixel((32, 32)) == (255, 255, 255, 255)


def test_fast_mode_progress_coalesces_thresholds_to_highest_percentage():
    nails = [(32 + x, 32 + y) for x, y in calculate_pegs(30, 32)]
    checkpoints = []
    animator.fast_mode(
        Image.new("RGB", (64, 64), "white"),
        Image.new("L", (64, 64), 0),
        nails,
        max_lines=1,
        progress_callback=lambda percentage, image: checkpoints.append(percentage),
    )
    assert checkpoints == [80]


def test_default_line_budget_reports_all_progress_checkpoints():
    nails = [(32 + x, 32 + y) for x, y in calculate_pegs(30, 32)]
    percentages = []
    animator.fast_mode(
        Image.new("RGB", (64, 64), "white"),
        Image.new("L", (64, 64), 0),
        nails,
        progress_callback=lambda percentage, image: percentages.append(percentage),
    )
    assert percentages == [20, 40, 60, 80]


@pytest.mark.parametrize(
    ("alpha", "checkpoint_values", "final_value"),
    [
        (0, [255, 255, 255, 255], 255),
        (60, [195, 149, 114, 87], 67),
        (255, [0, 0, 0, 0], 0),
    ],
)
def test_repeated_rendered_strokes_accumulate_opacity(
    alpha, checkpoint_values, final_value
):
    nails = [(0, 1)] * 11 + [(7, 1)] * 11
    values = []
    result = animator.fast_mode(
        Image.new("RGB", (8, 3), "white"),
        Image.new("L", (8, 3), 0),
        nails,
        max_lines=5,
        stroke_alpha=alpha,
        progress_callback=lambda percentage, snapshot: values.append(
            snapshot.getpixel((3, 1))[0]
        ),
    )
    assert values == checkpoint_values
    assert result.getpixel((3, 1)) == (final_value, final_value, final_value, 255)
    assert result.getpixel((3, 0)) == (255, 255, 255, 255)
