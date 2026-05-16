"""Module for selecting an input image using a graphical file dialog.

This module provides functionality to open a file dialog window and allow the
user to select an image file. The selected image path is then returned for
further processing.
"""

import logging
from pathlib import Path
from tkinter import Tk, filedialog
from typing import Optional


def select(tk_root: Tk) -> Optional[Path]:
    """Select an image to be used as the input image for the model

    This function is refactored to a functional programming style, avoiding side-effects
    and relying on pure functions.

    Returns:
        Optional[Path]: The path to the selected image or None if no image is selected
    """

    # Open file dialog for image selection
    file_path = filedialog.askopenfilename(
        parent=tk_root,
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")],
        defaultextension=".jpg",
        title="Select an image",
        initialdir=".",
    )

    # Return None if no image is selected
    if not file_path:
        logging.info("No image selected")
        return None

    logging.debug("Selected image: %s", file_path)
    return Path(file_path).resolve()
