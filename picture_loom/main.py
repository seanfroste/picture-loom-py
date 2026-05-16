import logging
from typing import Optional

import tkinter as tk
from PIL import Image

# Use rich_click for nicer Click output; it's a drop-in wrapper around Click
import rich_click as click

from .img_proc import cropper, grayscaler, resizer, round_mask
from .img_selector import image_select
from .weaver import gui, loom
from .logging_config import init_logging


@click.command()
@click.option("--crop/--no-crop", default=True, help="Enable or disable cropping")
@click.option("--resize", default=resizer.RESIZE_DIM, type=int, help="Resize dimension")
@click.option("-v", "--verbose", count=True, help="Increase verbosity (use -v for DEBUG)")
def main(crop: bool, resize: int, verbose: int) -> None:
    """Main CLI entrypoint for picture-loom."""
    # Initialize logging as early as possible
    init_logging(verbose)

    # Create root window for Tkinter
    root = tk.Tk()

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
            if crop:
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

                root.destroy()

            # grayscale the result
            gray_image = grayscaler.grayscale_img(cropped_img)

            logging.info("Image has been grayscaled")

            round_image = round_mask.apply(gray_image)

            logging.info("Image has been rounded out")

            resized_image = resizer.resize_img(round_image, resize)

            logging.info("Image has been resized")

            gui_root = tk.Tk()
            loom_gui = gui.LoomGUI(gui_root)
            gui_root.mainloop()

            num_pegs = loom_gui.get_num_pegs()
            logging.debug("Number of pegs: %d", num_pegs)

            loom.weave(resized_image, num_pegs)
