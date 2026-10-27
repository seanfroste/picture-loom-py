"""Module for the main drawing surface"""

# weaver/loom.py

# import atexit
# import turtle
# import os
import math
import tkinter as tk
from collections.abc import Callable

from PIL import Image, ImageDraw


def make_thumbnail(image: Image.Image, factor: int) -> Image.Image:
    """Create a thumbnail copy sized by the supplied reduction factor.

    Args:
        image: Source image to copy and reduce.
        factor: Divisor applied to each source dimension.

    Returns:
        A reduced copy of the source image.
    """
    thn = image.copy()
    thn.thumbnail(
        (image.size[0] // factor, image.size[1] // factor), Image.Resampling.BOX
    )
    return thn


def calculate_pegs(radius: int, num_pegs: int) -> list[tuple[int, int]]:
    """Calculate evenly spaced peg offsets around a circle.

    Args:
        radius: Circle radius in pixels.
        num_pegs: Number of peg positions to calculate.

    Returns:
        Peg offsets in circular order.
    """
    return [
        (
            int(radius * math.cos(i * 2 * math.pi / num_pegs)),
            int(radius * math.sin(i * 2 * math.pi / num_pegs)),
        )
        for i in range(num_pegs)
    ]


def draw_pegs(image: Image.Image, num_pegs: int) -> Image.Image:
    """Draw pegs in place on an image.

    Args:
        image: Board image to modify.
        num_pegs: Number of pegs to draw around the image center.

    Returns:
        The modified board image.
    """
    pegs_list = calculate_pegs(image.size[0] // 2, num_pegs)

    center_x = image.size[0] // 2
    center_y = image.size[1] // 2

    draw = ImageDraw.Draw(image)
    for i in pegs_list:
        draw.ellipse(
            (
                (
                    center_x + i[0] - 2,
                    center_y + i[1] - 2,
                ),
                (
                    center_x + i[0] + 2,
                    center_y + i[1] + 2,
                ),
            ),
            fill="black",
            outline=None,
        )

    return image


def make_board(image: Image.Image, num_pegs: int) -> Image.Image:
    """
    Creates a board with the specified image and number of pegs.

    Args:
        image (Image.Image): The image to be used for reference
        num_pegs (int): The number of pegs to be drawn on the board

    Returns:
        Image.Image: The generated board with pegs as a PIL Image object
    """
    thn = make_thumbnail(image, 8)

    # create base background
    base = Image.new("RGB", image.size, "grey")

    # create board base
    # board = Image.new("RGB", image.size, "grey")

    # draw white circle on board
    draw = ImageDraw.Draw(base)
    draw.ellipse(((0, 0), image.size), fill="white", outline="white")

    # show board and thumbnail
    # base.paste(board, (0, 0))
    base.paste(thn, (0, 0))

    base = draw_pegs(base, num_pegs)

    return base


# def delete_temp():
#     temp_file = "thumbnail.gif"
#     if os.path.exists(temp_file):
#         os.remove(temp_file)


def weave(
    image: Image.Image,
    num_pegs: int,
    *,
    max_lines: int = 5000,
    stroke_alpha: int = 60,
    delay_ms: int = 20,
    fast: bool = False,
    progress_callback: Callable[[int, Image.Image], None] | None = None,
) -> Image.Image | None:
    """Render a woven board, optionally returning its headless composite.

    Args:
        image: Processed image used to build and score the board.
        num_pegs: Number of pegs placed around the board.
        max_lines: Maximum number of string segments to render.
        stroke_alpha: String opacity from 0 through 255.
        delay_ms: Delay between GUI animation steps in milliseconds.
        fast: Render without creating a GUI window.
        progress_callback: Optional fast-mode checkpoint callback.

    Returns:
        The final composite in fast mode, or None after GUI animation.
    """
    base = make_board(image, num_pegs)
    center_x = image.size[0] // 2
    center_y = image.size[1] // 2
    pegs = calculate_pegs(image.size[0] // 2, num_pegs)
    nails = [(center_x + peg[0], center_y + peg[1]) for peg in pegs]

    from . import animator

    if fast:
        return animator.fast_mode(
            base,
            image,
            nails,
            max_lines=max_lines,
            stroke_alpha=stroke_alpha,
            progress_callback=progress_callback,
        )

    root = tk.Tk()
    canvas = tk.Canvas(master=root, width=image.size[0], height=image.size[1])
    canvas.pack()
    animator.run(
        root,
        canvas,
        base,
        image,
        nails,
        max_lines=max_lines,
        stroke_alpha=stroke_alpha,
        delay_ms=delay_ms,
    )
    root.mainloop()
    return None


if __name__ == "__main__":
    # When run as a script, avoid reconfiguring logging unconditionally.
    with Image.open("sample0.png") as img:
        cropped = img.crop((0, 0, min(img.size), min(img.size)))
        resized = cropped.resize((512, 512), Image.Resampling.BOX).convert("L")
        weave(resized, 360)
