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

    # def create_blank_root() -> Tk:
    #     """Create a root window

    #     Returns:
    #         Tk: The root window
    #     """
    #     root = Tk()
    #     root.withdraw()
    #     return root

    def get_file_path(root: Tk) -> Optional[str]:
        """Get the path to a file

        Args:
            root (Tk): The root window

        Returns:
            Optional[str]: The path to the selected file or None if no file is selected
        """
        return filedialog.askopenfilename(
            parent=root,
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")],
            defaultextension=".jpg",
            title="Select an image",
            initialdir=".",
        )

    # root = create_blank_root()
    file_path = get_file_path(tk_root)

    if not file_path:
        logging.info("No image selected")
        return None

    logging.debug("Selected image: %s", file_path)
    return Path(file_path)
