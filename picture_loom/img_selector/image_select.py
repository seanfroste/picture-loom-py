"""Module for selecting an input image using a graphical file dialog.

This module provides functionality to open a file dialog window and allow the
user to select an image file. The selected image path is then returned for
further processing.
"""

import logging
from pathlib import Path
from tkinter import Tk, filedialog


def select(tk_root: Tk) -> Path | None:
    """
    Opens a file dialog for the user to select an image file. The function returns the path of the selected image or None if no image is selected.

    Args:
        tk_root (Tk): The root Tkinter window to which the file dialog will be attached.

    Returns:
        Path | None: The resolved path of the selected image file, or None if no file was selected.
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
