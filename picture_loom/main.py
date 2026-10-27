"""Command-line interface for preparing and rendering Picture Loom images."""

import hashlib
import io
import logging
import re
import tkinter as tk
from pathlib import Path

import rich_click as click
from click.exceptions import Abort
from PIL import Image

from . import __version__
from .img_proc import cropper, grayscaler, resizer, round_mask
from .img_selector import image_select
from .logging_config import init_logging
from .weaver import gui, loom


@click.command(
    context_settings={"help_option_names": ["-h", "--help"]},
    help="Convert an image into a circular weaving loom pattern.",
)
@click.version_option(version=__version__)
@click.option("--crop/--no-crop", default=True, help="Enable or disable cropping")
@click.option("--resize", default=512, type=int, help="Resize dimension")
@click.option(
    "-v", "--verbose", count=True, help="Increase verbosity (use -v for DEBUG)"
)
@click.option("--pegs", "peg_count", type=int, default=None, help="Number of pegs")
@click.option(
    "--max-lines", default=5000, type=int, help="Maximum number of string lines"
)
@click.option("--stroke-alpha", default=60, type=int, help="Stroke alpha (0-255)")
@click.option("--delay-ms", default=20, type=int, help="Delay between animation steps")
@click.option("--fast", is_flag=True, default=False, help="Run non-GUI batch mode")
@click.option(
    "-i",
    "--input",
    "input_path",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
    default=None,
    help="Input image path (skip file dialog)",
)
@click.option(
    "-o",
    "--output",
    "output_path",
    type=click.Path(path_type=Path, dir_okay=False),
    default=None,
    help="Exact output image path",
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    default=False,
    help="Overwrite output without prompting",
)
def main(
    crop: bool,
    resize: int,
    verbose: int,
    peg_count: int | None,
    max_lines: int,
    stroke_alpha: int,
    delay_ms: int,
    fast: bool,
    input_path: Path | None,
    output_path: Path | None,
    force: bool,
) -> None:
    """Convert a processed image into a circular string-art loom pattern.

    Args:
        crop: Whether to crop the selected image.
        resize: Output image side length in pixels.
        verbose: Logging verbosity count.
        peg_count: Number of pegs, or None to prompt interactively.
        max_lines: Maximum number of string segments.
        stroke_alpha: Rendered string opacity from 0 through 255.
        delay_ms: Delay between GUI animation steps in milliseconds.
        fast: Render headlessly and save the resulting PNG.
        input_path: Input image path, or None to open the file chooser.
        output_path: Exact output path, or None for a content-addressed path.
        force: Overwrite an existing output without prompting.

    Returns:
        None.
    """
    if fast and (input_path is None or peg_count is None):
        raise click.UsageError("--fast requires --input and --pegs")
    init_logging(verbose)

    if input_path is None:
        root = tk.Tk()
        input_image_path = image_select.select(root)
        root.destroy()
        if input_image_path is None:
            return
    else:
        input_image_path = input_path

    with Image.open(input_image_path) as img:
        logging.info("Original Image size: %dx%d", img.width, img.height)
        if input_path is not None:
            if crop:
                min_dim = min(img.width, img.height)
                left = (img.width - min_dim) // 2
                top = (img.height - min_dim) // 2
                cropped_img = img.crop((left, top, left + min_dim, top + min_dim))
            else:
                cropped_img = img.copy()
        elif not crop:
            cropped_img = img.copy()
        else:
            crop_root = tk.Tk()
            img_cropper = cropper.ImageCropperUI(crop_root, img)
            img_cropper.root.mainloop()
            if img_cropper.cropped_image is None:
                logging.info("Cropping was cancelled")
                return
            cropped_img = img_cropper.cropped_image

        gray_image = grayscaler.grayscale_img(cropped_img)
        round_image = round_mask.apply(gray_image)
        resized_image = resizer.resize_img(round_image, resize)

    if peg_count is None:
        gui_root = tk.Tk()
        loom_gui = gui.LoomGUI(gui_root)
        gui_root.mainloop()
        peg_count = loom_gui.get_num_pegs()

    progress_images: dict[int, Image.Image] = {}

    def capture_progress(percentage: int, snapshot: Image.Image) -> None:
        """Retain a completed fast-render checkpoint for later persistence."""
        progress_images[percentage] = snapshot

    batch_image = loom.weave(
        resized_image,
        peg_count,
        max_lines=max_lines,
        stroke_alpha=stroke_alpha,
        delay_ms=delay_ms,
        fast=fast,
        progress_callback=capture_progress if fast else None,
    )
    if fast and batch_image is not None:
        saved_path = _save_output(batch_image, output_path, force=force)
        if saved_path is not None:
            progress_dir = saved_path.with_name(f"{saved_path.stem}-progress")
            if progress_images:
                progress_dir.mkdir(parents=True, exist_ok=True)
                for percentage, snapshot in progress_images.items():
                    snapshot.save(progress_dir / f"{percentage}-percent.png")
            logging.info("Saved output to %s", saved_path)


def _save_output(
    image: Image.Image, output_path: Path | None, *, force: bool = False
) -> Path | None:
    """Save a PNG, resolving collisions and returning its actual destination.
    Args:
        image: Image to encode as PNG.
        output_path: Exact destination, or None to choose a content-addressed path.
        force: Whether to replace an existing destination without prompting.

    Returns:
        The written path, or None if the collision prompt was cancelled.
    """
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    png_bytes = buffer.getvalue()
    target = output_path
    if target is None:
        digest = hashlib.sha256(png_bytes).hexdigest()
        target = Path("out") / f"{digest[:10]}.png"
    target.parent.mkdir(parents=True, exist_ok=True)

    if force:
        target.write_bytes(png_bytes)
        return target

    base_target = target
    while True:
        if target.exists():
            try:
                choice = click.prompt(
                    f"Output {target} exists; choose overwrite, numbered-duplicate, or cancel",
                    type=click.Choice(
                        ["overwrite", "numbered-duplicate", "cancel"],
                        case_sensitive=False,
                    ),
                    default="cancel",
                )
            except (EOFError, OSError, Abort) as exc:
                raise click.ClickException(
                    "stdin unavailable; use --force or a non-colliding --output"
                ) from exc
            if choice == "cancel":
                return None
            if choice == "overwrite":
                target.write_bytes(png_bytes)
                return target
            pattern = re.compile(
                rf"{re.escape(base_target.stem)}-(\d+)"
                rf"{re.escape(base_target.suffix)}"
            )
            numbers = [
                int(match.group(1))
                for sibling in base_target.parent.iterdir()
                if (match := pattern.fullmatch(sibling.name)) is not None
            ]
            target = base_target.with_name(
                f"{base_target.stem}-{max(numbers, default=0) + 1}"
                f"{base_target.suffix}"
            )
            continue

        try:
            with target.open("xb") as output:
                output.write(png_bytes)
        except FileExistsError:
            continue
        return target
