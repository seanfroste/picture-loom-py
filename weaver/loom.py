"""Module for the main drawing surface"""

# weaver/loom.py

# import atexit
# import turtle
# import os
import logging
import math
import tkinter as tk

from PIL import Image, ImageDraw, ImageTk


def make_thumbnail(image: Image.Image, factor: int) -> Image.Image:
    thn = image.copy()
    thn.thumbnail(
        (image.size[0] // factor, image.size[1] // factor), Image.Resampling.BOX
    )
    return thn


def calculate_pegs(radius: int, num_pegs: int) -> list[tuple[int, int]]:
    return [
        (
            int(radius * math.cos(i * 2 * math.pi / num_pegs)),
            int(radius * math.sin(i * 2 * math.pi / num_pegs)),
        )
        for i in range(num_pegs)
    ]


def draw_pegs(image: Image.Image, num_pegs: int) -> Image.Image:
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


def weave(image: Image.Image, num_pegs: int) -> None:
    root = tk.Tk()
    canvas = tk.Canvas(master=root, width=image.size[0], height=image.size[1])

    base = make_board(image, num_pegs)

    # # save background temporarily for use with turtle bgpic
    # base.save("thumbnail.gif", "GIF")
    # atexit.register(delete_temp)

    # # set background
    # shuttle.screen.bgpic("thumbnail.gif")

    backdrop = ImageTk.PhotoImage(base)

    canvas.create_image(0, 0, anchor=tk.NW, image=backdrop)
    canvas.pack()

    # turtle.done()
    root.mainloop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    with Image.open("sample0.png") as img:
        img = img.crop((0, 0, min(img.size), min(img.size)))
        img = img.resize((512, 512), Image.Resampling.BOX).convert("L")
        weave(img, 360)
