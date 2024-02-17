"""Module for the main drawing surface"""

# weaver/loom.py

import atexit
import os
import turtle

from PIL import Image, ImageDraw


def make_thumbnail(image: Image.Image, factor: int) -> Image.Image:
    thn = image.copy()
    thn.thumbnail(
        (image.size[0] // factor, image.size[1] // factor), Image.Resampling.BOX
    )
    return thn


def make_board(image: Image.Image) -> Image.Image:
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

    return base


def delete_temp():
    temp_file = "thumbnail.gif"
    if os.path.exists(temp_file):
        os.remove(temp_file)


def run(image: Image.Image) -> None:
    shuttle = turtle.Turtle()
    shuttle.penup()
    shuttle.hideturtle()
    turtle.Screen().setup(image.size[0] + 10, image.size[1] + 10)

    # create thumbnail
    thn = image.copy()
    thn.thumbnail(
        (image.size[0] // 8, image.size[1] // 8),
        Image.Resampling.BOX,
    )

    # create background
    base = make_board(image)

    # save background temporarily for use with turtle bgpic
    base.save("thumbnail.gif", "GIF")
    atexit.register(delete_temp)

    shuttle.screen.screensize(
        canvwidth=image.size[0],
        canvheight=image.size[1],
        bg="grey",
    )

    # set background
    shuttle.screen.bgpic("thumbnail.gif")

    turtle.done()


if __name__ == "__main__":
    with Image.open("sample0.png") as img:
        img = img.crop((0, 0, min(img.size), min(img.size)))
        img = img.resize((512, 512), Image.Resampling.BOX)
        run(img)
