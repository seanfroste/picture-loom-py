import os
import sys
from pathlib import Path

from PIL import Image, ImageFont, ImageOps

font = ImageFont.truetype(".\\Kalam-Bold.ttf", size=10)

created_files = []


def convert_image(infile_path: Path) -> Path:
    with Image.open(infile_path.resolve()) as im:
        gray = ImageOps.grayscale(image=im)

        width, height = gray.size
        box_len = min(width, height)
        left = (box_len / 2) - (width / 2)
        right = (box_len / 2) + (width / 2)
        top = (box_len / 2) - (height / 2)
        bottom = (box_len / 2) + (height / 2)

        square = gray.crop((left, top, right, bottom))

        large = ImageOps.scale(
            square, ((1024 / box_len) + 1), resample=Image.Resampling.BOX
        )

        better_file_stem = infile_path.stem

        while "\t" in better_file_stem:
            better_file_stem = better_file_stem.replace("\t", " ")

        while "  " in better_file_stem:
            better_file_stem = better_file_stem.replace("  ", " ")

        while " " in better_file_stem:
            better_file_stem = better_file_stem.replace(" ", "-")

        while "_" in better_file_stem:
            better_file_stem = better_file_stem.replace("_", "-")

        outfile_path = Path(better_file_stem + "_remade" + ".bmp")

        if outfile_path.exists():
            os.remove(outfile_path.resolve())

        large.save(outfile_path.resolve(), bitmap_format="bmp")

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
