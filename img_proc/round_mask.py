"""Module for applying a round mask to an image"""

from PIL import Image, ImageDraw


def apply(input_image: Image.Image) -> Image.Image:
    """
    Apply an ellipse mask to the input image and return the result.

    Args:
    input_image (Image.Image): The input image to be masked.

    Returns:
    Image.Image: The resulting masked image.
    """
    # Get the size of the input image
    image_size = input_image.size

    # Create a new blank RGBA image with transparent background
    result_image = Image.new("RGBA", image_size, (0, 0, 0, 0))

    # Create a mask with a white filled ellipse
    mask_image = Image.new("L", image_size, 0)
    draw = ImageDraw.Draw(mask_image)
    draw.ellipse(((0, 0), image_size), fill=255)

    # Composite the input image with the mask
    result_image.paste(input_image, (0, 0), mask_image)

    return result_image


if __name__ == "__main__":
    with Image.open("sample0.png") as img:
        img = img.crop((0, 0, min(img.size), min(img.size)))
        roundy = apply(img)
        roundy.show()
