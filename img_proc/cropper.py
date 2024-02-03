# img_proc/image_cropper.py
from tkinter import TOP, Button, Canvas, Label, Tk
from typing import Optional

from PIL import Image, ImageTk


class CropperCanvas:

    def __init__(self, tk_root: Tk, image: Image.Image):
        self.canvas: Canvas = Canvas(tk_root, width=image.width, height=image.height)
        self.tk_image = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        self.canvas.pack()
        self.start_x: int = 0
        self.start_y: int = 0
        self.rect_id: Optional[int] = None

    def set_starting_point(self, x: int, y: int):
        self.start_x = x
        self.start_y = y

    def update_rectangle(self, start_x: int, start_y: int, end_x: int, end_y: int):
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(
            start_x, start_y, end_x, end_y, outline="green"
        )


class ImageCropperUI:
    def __init__(self, tk_root: Tk, image: Image.Image) -> None:
        self.root: Tk = tk_root
        self.root.title("Image Cropper")

        self.image: Image.Image = image
        self.canvas_handler = CropperCanvas(tk_root, image)

        self.canvas_handler.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas_handler.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas_handler.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.confirm_preview_button: Button = Button(
            tk_root, text="Confirm Preview", command=self.confirm_preview
        )
        self.confirm_preview_button.pack(side=TOP)

        self.confirm_crop_button: Button = Button(
            tk_root, text="Confirm Crop", command=self.confirm_crop
        )
        self.confirm_crop_button.pack(side=TOP)
        self.confirm_crop_button["state"] = "disabled"

        self.cropped_image: Optional[Image.Image] = None
        self.preview_tk_image: Optional[ImageTk.PhotoImage] = None

        self.preview_label: Optional[Label] = None

    def on_press(self, event) -> None:
        x, y = self.canvas_handler.canvas.canvasx(
            event.x
        ), self.canvas_handler.canvas.canvasy(event.y)
        self.canvas_handler.set_starting_point(x, y)

    def on_drag(self, event) -> None:
        cur_x, cur_y = self.canvas_handler.canvas.canvasx(
            event.x
        ), self.canvas_handler.canvas.canvasy(event.y)
        side_length = min(
            abs(cur_x - self.canvas_handler.start_x),
            abs(cur_y - self.canvas_handler.start_y),
        )

        end_x = (
            self.canvas_handler.start_x + side_length
            if cur_x > self.canvas_handler.start_x
            else self.canvas_handler.start_x - side_length
        )
        end_y = (
            self.canvas_handler.start_y + side_length
            if cur_y > self.canvas_handler.start_y
            else self.canvas_handler.start_y - side_length
        )

        if self.canvas_handler.rect_id:
            self.canvas_handler.canvas.delete(self.canvas_handler.rect_id)
        self.canvas_handler.rect_id = self.canvas_handler.canvas.create_rectangle(
            self.canvas_handler.start_x,
            self.canvas_handler.start_y,
            end_x,
            end_y,
            outline="green",
        )

    def on_release(self, event) -> None:
        cur_x, cur_y = self.canvas_handler.canvas.canvasx(
            event.x
        ), self.canvas_handler.canvas.canvasy(event.y)
        side_length = min(
            abs(cur_x - self.canvas_handler.start_x),
            abs(cur_y - self.canvas_handler.start_y),
        )
        end_x = (
            self.canvas_handler.start_x + side_length
            if cur_x > self.canvas_handler.start_x
            else self.canvas_handler.start_x - side_length
        )
        end_y = (
            self.canvas_handler.start_y + side_length
            if cur_y > self.canvas_handler.start_y
            else self.canvas_handler.start_y - side_length
        )

        self.cropped_image = self.image.crop(
            (
                min(self.canvas_handler.start_x, end_x),
                min(self.canvas_handler.start_y, end_y),
                max(self.canvas_handler.start_x, end_x),
                max(self.canvas_handler.start_y, end_y),
            )
        )

        # Enable the "Confirm Crop" button for finalizing the crop
        self.confirm_crop_button["state"] = "normal"

    def confirm_preview(self) -> None:
        # Display the preview label with the cropped image
        if self.cropped_image:
            self.preview_tk_image = ImageTk.PhotoImage(self.cropped_image)
            if self.preview_label:
                self.preview_label.destroy()
            self.preview_label = Label(
                self.root, image=self.preview_tk_image, padx=10, pady=10
            )
            self.preview_label.pack()

            # Enable the "Confirm Crop" button after previewing
            self.confirm_crop_button["state"] = "normal"

    def confirm_crop(self) -> None:
        # You can use self.cropped_image as needed (e.g., save, display, etc.)
        if self.cropped_image:
            self.cropped_image.show()
            self.root.destroy()


if __name__ == "__main__":
    input_image_path: str = "sample0.png"
    original_image: Image.Image = Image.open(input_image_path)

    root: Tk = Tk()
    cropper_ui: ImageCropperUI = ImageCropperUI(root, original_image)
    root.mainloop()
