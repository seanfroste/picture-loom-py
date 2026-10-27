"""Convert source images to grayscale for string-art scoring."""

# img_proc/grayscaler.py

from PIL import Image


def grayscale_img(image: Image.Image) -> Image.Image:
    """
    Converts the input image to grayscale using the "L" mode in PIL.

    Args:
        image (Image.Image): The input image to be converted to grayscale.

    Returns:
        Image.Image: A new image in grayscale mode.
    """
    return image.convert("L")


if __name__ == "__main__":
    with Image.open("sample0.png") as img:
        grey = grayscale_img(img)
        grey.show()
