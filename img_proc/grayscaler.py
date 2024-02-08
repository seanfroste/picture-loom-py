# img_proc/grayscaler.py

from PIL import Image


def grayscale_img(image: Image.Image) -> Image.Image:
    return image.convert("L")


if __name__ == "__main__":
    with Image.open("sample0.png") as img:
        grey = grayscale_img(img)
        grey.show()
