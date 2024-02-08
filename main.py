"""
Main program
"""

import argparse
import logging
from tkinter import Tk

from PIL import Image

from img_proc import cropper, grayscaler
from img_selector import image_select


def main() -> None:
    """
    Main function
    No parameters. Returns None.
    """
    root = Tk()
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument("--crop", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    input_image_path = image_select.select(root)

    cropped_img: Image.Image = Image.new("RGB", (100, 100), color="white")
    gray_image: Image.Image = Image.new("RGB", (100, 100), color="white")

    if input_image_path and input_image_path.is_file():
        with Image.open(input_image_path) as img:
            logging.info("Original Image size: %dx%d", img.width, img.height)

            if args.crop:
                img_cropper = cropper.ImageCropperUI(root, img)

                root.mainloop()

                logging.debug("crop UI initialized")

                if img_cropper.cropped_image:
                    cropped_img = img_cropper.cropped_image

                    logging.debug(type(cropped_img))
                    logging.info(
                        "Cropped image is of dimensions %dx%d",
                        cropped_img.width,
                        cropped_img.height,
                    )
                else:
                    logging.debug("Cropped image is None")

            else:
                min_dim = min(img.width, img.height)
                cropped_img = img.crop((0, 0, min_dim, min_dim))

                logging.info("Default cropping applied")
                logging.info(
                    "Cropped image is of dimensions %dx%d",
                    cropped_img.width,
                    cropped_img.height,
                )

            # cropped_img.show()
            gray_image = grayscaler.grayscale_img(cropped_img)

            logging.debug("Image has been grayscaled")
            gray_image.show()


if __name__ == "__main__":
    main()
