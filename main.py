"""
Main program
"""

import logging
from tkinter import Tk

from PIL import Image

from img_proc import cropper
from img_selector import image_select


def main() -> None:
    """
    Main function
    No parameters. Returns None.
    """
    root = Tk()
    logging.basicConfig(level=logging.DEBUG)
    input_image_path = image_select.select(root)

    cropped_img: Image.Image

    if input_image_path and input_image_path.is_file():
        with Image.open(input_image_path) as img:
            logging.debug("Image size: %dx%d", img.width, img.height)

            img_cropper = cropper.ImageCropperUI(root, img)

            root.mainloop()

            logging.debug("crop UI initialized")

            if img_cropper.cropped_image:
                cropped_img = img_cropper.cropped_image
                logging.debug(type(cropped_img))
                logging.info("The image has been cropped")
            else:
                logging.debug("Cropped image is None")


if __name__ == "__main__":
    main()
