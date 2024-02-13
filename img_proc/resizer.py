"""Module for resizing an image"""

from PIL import Image

RESIZE_DIM = 512


def resize_img(image: Image.Image, size: int) -> Image.Image:
    return image.resize(
        (size, size),
        resample=(
            Image.Resampling.LANCZOS
            if image.mode == "RGB"
            else Image.Resampling.NEAREST
        ),
    )


if __name__ == "__main__":
    with Image.open("sample0.png") as img:
        print(img.size)
        cropped_img = img.crop((0, 0, min(img.size), min(img.size)))
        resized = resize_img(cropped_img, RESIZE_DIM)
        resized.show()
