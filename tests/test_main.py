import hashlib
import io
from pathlib import Path

import pytest
from click.testing import CliRunner
from PIL import Image

from picture_loom import main as main_module


def test_default_output_uses_final_png_digest_and_creates_parent(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    image = Image.new("RGB", (3, 2), "navy")
    destination = main_module._save_output(image, None)
    payload = io.BytesIO()
    image.save(payload, format="PNG")
    assert (
        destination
        == Path("out")
        / f"{hashlib.sha256(payload.getvalue()).hexdigest()[:10]}.png"
    )
    assert destination is not None
    assert destination.read_bytes() == payload.getvalue()


def test_explicit_path_and_duplicate_after_highest_suffix(tmp_path, monkeypatch):
    target = tmp_path / "image.png"
    target.write_bytes(b"existing")
    (tmp_path / "image-2.png").write_bytes(b"two")
    (tmp_path / "image-7.png").write_bytes(b"seven")
    monkeypatch.setattr(
        main_module.click, "prompt", lambda *args, **kwargs: "numbered-duplicate"
    )
    saved = main_module._save_output(Image.new("RGB", (1, 1)), target)
    assert saved == tmp_path / "image-8.png"
    assert saved is not None
    assert target.read_bytes() == b"existing"
    assert Image.open(saved).size == (1, 1)


def test_cancel_preserves_collision_bytes(tmp_path, monkeypatch):
    target = tmp_path / "same.png"
    target.write_bytes(b"user data")
    monkeypatch.setattr(main_module.click, "prompt", lambda *args, **kwargs: "cancel")
    assert main_module._save_output(Image.new("RGB", (1, 1)), target) is None
    assert target.read_bytes() == b"user data"


def test_overwrite_replaces_exact_target(tmp_path, monkeypatch):
    target = tmp_path / "same.png"
    target.write_bytes(b"user data")
    monkeypatch.setattr(
        main_module.click, "prompt", lambda *args, **kwargs: "overwrite"
    )
    assert main_module._save_output(Image.new("RGB", (1, 1)), target) == target
    assert Image.open(target).size == (1, 1)


def test_force_replaces_exact_target_without_prompt(tmp_path, monkeypatch):
    target = tmp_path / "same.png"
    target.write_bytes(b"user data")
    monkeypatch.setattr(
        main_module.click,
        "prompt",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError()),
    )
    assert (
        main_module._save_output(Image.new("RGB", (1, 1)), target, force=True) == target
    )
    assert Image.open(target).size == (1, 1)


def test_fast_requires_input_and_pegs_before_tk(monkeypatch):
    def forbidden_tk():
        raise AssertionError("Tk was constructed")

    monkeypatch.setattr(main_module.tk, "Tk", forbidden_tk)
    cli_result = CliRunner().invoke(main_module.main, ["--fast"])
    assert cli_result.exit_code == 2
    assert "--fast requires --input and --pegs" in cli_result.output


@pytest.mark.parametrize(
    "arguments", [["--fast", "--pegs", "22"], ["--fast", "--input", "img/sample1.png"]]
)
def test_fast_requires_both_arguments(arguments):
    cli_result = CliRunner().invoke(main_module.main, arguments)
    assert cli_result.exit_code == 2
    assert "--fast requires --input and --pegs" in cli_result.output


def test_closed_stdin_refuses_collision_without_modifying_target(tmp_path, monkeypatch):
    target = tmp_path / "same.png"
    target.write_bytes(b"user data")

    def closed_stdin(*args, **kwargs):
        raise OSError("stdin is closed")

    monkeypatch.setattr(main_module.click, "prompt", closed_stdin)
    with pytest.raises(main_module.click.ClickException, match="--force"):
        main_module._save_output(Image.new("RGB", (1, 1)), target)
    assert target.read_bytes() == b"user data"


def test_interactive_no_crop_skips_cropper_and_copies_selected_image(
    tmp_path, monkeypatch
):
    image_path = tmp_path / "source.png"
    Image.new("RGB", (12, 8), "red").save(image_path)

    class Root:
        destroyed = False

        def destroy(self):
            self.destroyed = True

    root = Root()
    monkeypatch.setattr(main_module.tk, "Tk", lambda: root)
    monkeypatch.setattr(
        main_module.image_select, "select", lambda selected_root: image_path
    )
    monkeypatch.setattr(
        main_module.cropper,
        "ImageCropperUI",
        lambda *args: (_ for _ in ()).throw(AssertionError("cropper constructed")),
    )
    woven = []

    monkeypatch.setattr(
        main_module.loom,
        "weave",
        lambda image, pegs, **kwargs: woven.append(image.size),
    )
    cli_result = CliRunner().invoke(
        main_module.main,
        ["--no-crop", "--pegs", "22", "--resize", "8"],
    )
    assert cli_result.exit_code == 0, cli_result.output
    assert root.destroyed
    assert woven == [(8, 8)]


def test_interactive_crop_uses_cropper_root_and_cancellation_skips_weaving(
    tmp_path, monkeypatch
):
    image_path = tmp_path / "source.png"
    Image.new("RGB", (12, 8), "red").save(image_path)

    class Root:
        def __init__(self):
            self.mainloop_calls = 0

        def destroy(self):
            pass

        def mainloop(self):
            self.mainloop_calls += 1

    root = Root()
    monkeypatch.setattr(main_module.tk, "Tk", lambda: root)
    monkeypatch.setattr(
        main_module.image_select, "select", lambda selected_root: image_path
    )
    cropper_roots = []

    class CancelledCropper:
        cropped_image = None

        def __init__(self, crop_root, image):
            cropper_roots.append(crop_root)
            self.root = crop_root

    monkeypatch.setattr(main_module.cropper, "ImageCropperUI", CancelledCropper)
    monkeypatch.setattr(
        main_module.loom,
        "weave",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("weaving after cancel")
        ),
    )
    cli_result = CliRunner().invoke(main_module.main, ["--pegs", "22"])
    assert cli_result.exit_code == 0, cli_result.output
    assert cropper_roots == [root]
    assert root.mainloop_calls == 1


def test_file_dialog_cancellation_skips_weaving(monkeypatch):
    class Root:
        destroyed = False

        def destroy(self):
            self.destroyed = True

    root = Root()
    monkeypatch.setattr(main_module.tk, "Tk", lambda: root)
    monkeypatch.setattr(main_module.image_select, "select", lambda selected_root: None)
    monkeypatch.setattr(
        main_module.loom,
        "weave",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("weaving after file-dialog cancellation")
        ),
    )
    cli_result = CliRunner().invoke(main_module.main, [])
    assert cli_result.exit_code == 0, cli_result.output
    assert root.destroyed


def test_file_created_at_write_boundary_is_preserved(tmp_path, monkeypatch):
    target = tmp_path / "race.png"
    original_open = Path.open
    competing_write = False

    def race_open(path, mode="r", *args, **kwargs):
        nonlocal competing_write
        if path == target and mode in ("xb", "wb") and not competing_write:
            competing_write = True
            with original_open(path, "wb") as output:
                output.write(b"concurrent user file")
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", race_open)
    monkeypatch.setattr(
        main_module.click, "prompt", lambda *args, **kwargs: "numbered-duplicate"
    )
    saved_path = main_module._save_output(Image.new("RGB", (1, 1)), target)
    assert target.read_bytes() == b"concurrent user file"
    assert saved_path == tmp_path / "race-1.png"
    assert saved_path is not None
    assert Image.open(saved_path).size == (1, 1)


def test_progress_images_are_saved_next_to_the_actual_output(tmp_path, monkeypatch):
    source = tmp_path / "source.png"
    Image.new("RGB", (4, 4), "white").save(source)
    target = tmp_path / "woven.png"

    run = 0

    def weave(image, pegs, **kwargs):
        nonlocal run
        run += 1
        kwargs["progress_callback"](
            20, Image.new("RGB", (4, 4), "red" if run == 1 else "yellow")
        )
        kwargs["progress_callback"](40, Image.new("RGB", (4, 4), "blue"))
        return Image.new("RGB", (4, 4), "green")
    monkeypatch.setattr(main_module.loom, "weave", weave)
    result = CliRunner().invoke(
        main_module.main,
        [
            "--input",
            str(source),
            "--resize",
            "4",
            "--pegs",
            "22",
            "--fast",
            "--output",
            str(target),
            "--force",
        ],
    )
    assert result.exit_code == 0, result.output
    assert Image.open(target).getpixel((0, 0)) == (0, 128, 0)
    progress_dir = tmp_path / "woven-progress"
    assert Image.open(progress_dir / "20-percent.png").getpixel((0, 0)) == (255, 0, 0)
    assert Image.open(progress_dir / "40-percent.png").getpixel((0, 0)) == (0, 0, 255)
    replaced = CliRunner().invoke(
        main_module.main,
        [
            "--input",
            str(source),
            "--resize",
            "4",
            "--pegs",
            "22",
            "--fast",
            "--output",
            str(target),
            "--force",
        ],
    )
    assert replaced.exit_code == 0, replaced.output
    assert Image.open(progress_dir / "20-percent.png").getpixel((0, 0)) == (
        255,
        255,
        0,
    )


def test_cancelled_output_does_not_persist_progress(tmp_path, monkeypatch):
    source = tmp_path / "source.png"
    Image.new("RGB", (4, 4), "white").save(source)
    target = tmp_path / "woven.png"
    target.write_bytes(b"preserve")

    def weave(image, pegs, **kwargs):
        kwargs["progress_callback"](20, Image.new("RGB", (4, 4), "red"))
        return Image.new("RGB", (4, 4), "green")

    monkeypatch.setattr(main_module.loom, "weave", weave)
    monkeypatch.setattr(main_module.click, "prompt", lambda *args, **kwargs: "cancel")
    result = CliRunner().invoke(
        main_module.main,
        [
            "--input",
            str(source),
            "--resize",
            "4",
            "--pegs",
            "22",
            "--fast",
            "--output",
            str(target),
        ],
    )
    assert result.exit_code == 0, result.output
    assert target.read_bytes() == b"preserve"
    assert not (tmp_path / "woven-progress").exists()
