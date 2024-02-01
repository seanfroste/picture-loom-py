"""
Main program
"""

import logging

from PIL import Image

import img_select


def main() -> None:
    """
    Main function
    No parameters. Returns None.
    """
    logging.basicConfig(level=logging.DEBUG)
    input_image = img_select.select()

    if input_image:
        with Image.open(input_image) as image:
            image.show()


if __name__ == "__main__":
    main()
