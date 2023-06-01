import os
import string
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

font = ImageFont.truetype(".\\Kalam-Bold.ttf", size=10)

created_files = []


def convert_image(infile_path: Path) -> Path:
    with Image.open(infile_path.resolve()) as im:
        gray = ImageOps.grayscale(image=im)

        width, height = gray.size
        box_len = min(width, height)
        left = (width / 2) - (box_len / 2)
        right = (width / 2) + (box_len / 2)
        top = (height / 2) - (box_len / 2)
        bottom = (height / 2) + (box_len / 2)

        square = gray.crop((left, top, right, bottom))

        large = ImageOps.scale(
            square, ((1024 / box_len) + 1), resample=Image.Resampling.BOX
        )

        imArr = np.array(large)

        alph = Image.new("L", large.size, 0)
        draw = ImageDraw.Draw(alph)
        draw.pieslice([0, 0, large.size[0], large.size[1]], 0, 360, fill=255)

        arAlpha = np.array(alph)

        imArr = np.dstack((imArr, arAlpha))

        better_file_stem = infile_path.stem

        while "\t" in better_file_stem:
            better_file_stem = better_file_stem.replace("\t", " ")

        while "  " in better_file_stem:
            better_file_stem = better_file_stem.replace("  ", " ")

        while " " in better_file_stem:
            better_file_stem = better_file_stem.replace(" ", "-")

        while "_" in better_file_stem:
            better_file_stem = better_file_stem.replace("_", "-")

        file_stem_list = list(better_file_stem)

        for character in better_file_stem:
            if character not in (string.ascii_letters + "- "):
                file_stem_list.remove(character)

        better_file_stem = "".join(file_stem_list)

        outfile_path = Path(better_file_stem + "_remade" + ".png")

        if outfile_path.exists():
            os.remove(outfile_path.resolve())

        time.sleep(2)

        Image.fromarray(imArr).save(outfile_path.resolve(), bitmap_format="png")

    created_files.append(outfile_path.resolve())

    return outfile_path


def main() -> None:
    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    else:
        input_file = Path("./angry_nyanderer.png")
    gray = convert_image(input_file)

    with Image.open(gray.resolve()) as gray:
        gray.show()


if __name__ == "__main__":
    main()
