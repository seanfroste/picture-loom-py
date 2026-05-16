"""Module for the gui"""

# weaver/gui.py

import logging
import tkinter as tk


class LoomGUI:
    def __init__(self, tk_root: tk.Tk) -> None:
        """
        Initializes the LoomGUI class, which creates a GUI for selecting the number of pegs to be used in the picture loom. The GUI consists of a slider for selecting the number of pegs and a button to confirm the selection.

        Args:
            tk_root (tk.Tk): The root Tkinter window to which the GUI will be attached.
        """
        self.root = tk_root
        self.num_pegs: int = 0

        self.create_widgets()

    def create_widgets(self) -> None:
        """
        Creates the widgets for the GUI, including a slider for selecting the number of pegs and a button to confirm the selection.
        """
        self.num_pegs_slider = tk.Scale(
            self.root,
            from_=100,
            to=500,
            orient=tk.HORIZONTAL,
            resolution=10,
            label="Number of pegs",
        )
        self.num_pegs_slider.set(360)  # type: ignore
        self.num_pegs_slider.pack(
            padx=15,
            pady=15,
            expand=True,
            fill=tk.BOTH,
        )

        self.button = tk.Button(self.root, text="Done", command=self.on_button_click)
        self.button.pack(anchor=tk.SE, padx=10, pady=10)

    def on_button_click(self) -> None:
        """
        Event handler for the button click event. This function retrieves the value from the slider, stores it in the instance variable `num_pegs`, and then destroys the GUI window.
        """
        # get slider values
        self.num_pegs = int(self.num_pegs_slider.get())

        logging.debug("Number of pegs: %d", self.num_pegs)

        # destroy window
        self.root.destroy()

    def get_num_pegs(self) -> int:
        """
        Returns the number of pegs selected by the user.

        Returns:
            int: The number of pegs selected by the user.
        """
        # Return the value selected by the user
        return self.num_pegs


if __name__ == "__main__":
    root = tk.Tk()
    logging.basicConfig(level=logging.DEBUG)

    loom_gui = LoomGUI(root)

    root.mainloop()
    num_pegs = loom_gui.get_num_pegs()
    logging.debug("Number of pegs outside: %d", num_pegs)
