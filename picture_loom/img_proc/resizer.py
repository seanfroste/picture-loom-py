"""Module for resizing an image"""

from PIL import Image

# Constants
RESIZE_DIM = 512


def resize_img(image: Image.Image, size: int) -> Image.Image:
    """
    Resizes the input image to a square of the specified side length, using LANCZOS resampling for RGB images and NEAREST for others.

    Args:
        image (Image.Image): The input image to be resized.
        size (int): The side length of the square image.

    Returns:
        Image.Image: A new image resized to the specified square dimensions.
    """
    # Resize the image to the specified square side length
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
