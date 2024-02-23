"""
Main program
"""

import argparse
import logging
import tkinter as tk

from PIL import Image

from img_proc import cropper, grayscaler, resizer, round_mask
from img_selector import image_select
from weaver import gui, loom


def main() -> None:
    """
    Main function
    No parameters. Returns None.
    """
    # Create root window for Tkinter
    root = tk.Tk()

    # Set up logging
    logging.basicConfig(level=logging.DEBUG)

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--crop", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--resize", type=int, default=resizer.RESIZE_DIM)
    args = parser.parse_args()

    # Select an image using a file dialog
    input_image_path = image_select.select(root)

    # Initialize image variables
    cropped_img: Image.Image = Image.new("RGB", (100, 100), color="white")
    gray_image: Image.Image = Image.new("RGB", (100, 100), color="white")
    round_image: Image.Image = Image.new("RGB", (100, 100), color="white")
    resized_image: Image.Image = Image.new("RGB", (100, 100), color="white")

    # Process the image if it exists and is a file
    if input_image_path and input_image_path.is_file():
        with Image.open(input_image_path) as img:
            logging.info("Original Image size: %dx%d", img.width, img.height)

            # Check if cropping is required
            if args.crop:
                img_cropper = cropper.ImageCropperUI(root, img)

                # Run cropping UI
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
                    logging.error("Cropped image is None")

            else:
                # Apply default cropping to the selected image
                min_dim = min(img.width, img.height)
                cropped_img = img.crop((0, 0, min_dim, min_dim))

                logging.info("Default cropping applied")
                logging.debug(
                    "Cropped image is of dimensions %dx%d",
                    cropped_img.width,
                    cropped_img.height,
                )

            # cropped_img.show()

            # grayscale the result
            gray_image = grayscaler.grayscale_img(cropped_img)

            logging.info("Image has been grayscaled")
            # gray_image.show()

            round_image = round_mask.apply(gray_image)

            logging.info("Image has been rounded out")
            # round_image.show()

            resized_image = resizer.resize_img(round_image, args.resize)

            logging.info("Image has been resized")
            # resized_image.show()

            gui_root = tk.Tk()
            loom_gui = gui.LoomGUI(gui_root)
            gui_root.mainloop()

            num_pegs = loom_gui.get_num_pegs()
            logging.debug("Number of pegs: %d", num_pegs)

            loom.weave(resized_image, num_pegs)


if __name__ == "__main__":
    main()
