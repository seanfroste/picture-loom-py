# Picture Loom

An algorithmic generator for making string art out of digital images

## Table of Contents

- [Picture Loom](#picture-loom)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Contributing](#contributing)
  - [License](#license)

## Installation

Install the project and its development environment with uv:

```sh
uv sync
```

## Usage

`uv run picture-loom --help` (or `-h`) shows all options. `--version` reports
the installed package version.

```sh
# Interactive image selection, cropping, peg selection, and animated drawing
uv run picture-loom

# Reproducible headless batch run with an explicit output path
uv run picture-loom --input img/sample1.png --pegs 32 --max-lines 5000 \
  --fast --output result.png

# Supported alternate module entry point
python -m picture_loom --help
```

The primary command is `uv run picture-loom`; `python -m picture_loom` is also
supported. Without `--input`, the application opens an image chooser. With
cropping enabled (the default), a selected image opens the interactive cropper;
an image supplied with `--input` is center-cropped to a square instead. Use
`--no-crop` to skip cropping. If `--pegs` is omitted, the peg-count selector
opens. Normal mode animates the string drawing in a Tk window.

Fast mode is headless and requires both `--input` and `--pegs`. It writes the
final PNG to `--output` or defaults to
`out/<10-lowercase-hex-sha256>.png`, where the digest is computed from the
final PNG bytes. At a collision, choose `overwrite`, `numbered-duplicate`, or
`cancel` (default); numbered duplicates use the number after the highest
existing integer suffix. `--force` replaces the selected output path without
prompting. Explicit `--output` paths are preserved exactly.

For each fast render, thresholds are 20%, 40%, 60%, and 80% of the effective
line budget, including the default 5,000 lines; rounded-up thresholds are used.
When a tiny budget gives multiple milestones at the same completed line, one
checkpoint is saved with the highest crossed percentage. Reached checkpoints
are written beside the final image in `<saved-stem>-progress/`, as
`20-percent.png`, `40-percent.png`, `60-percent.png`, and `80-percent.png`.
For the default output, this is `out/<10-char-hash>-progress/`. A cancelled
final-output collision writes no progress images. If only one endpoint remains
eligible, later milestones can show the same image after repeated strokes reach
their configured opacity; with 22 pegs and a 10-index exclusion, only the
opposite peg is eligible at each step. A later successful run replaces
checkpoint files with matching names.

Options:

| Option | Default | Description |
| --- | --- | --- |
| `-i/--input IMAGE` | File chooser | Input image file; skips the file chooser. |
| `-o/--output PATH` | Content-addressed path | Exact PNG output path in fast mode. |
| `-v/--verbose` | INFO | One `-v` enables DEBUG logging. |
| `--crop/--no-crop` | Crop | Crop interactively for selected images; center-crop supplied images. |
| `--resize INTEGER` | `512` | Square output dimension. |
| `--pegs INTEGER` | Interactive selector | Number of pegs; omitted to select interactively. |
| `--max-lines INTEGER` | `5000` | Maximum number of drawn segments. |
| `--stroke-alpha INTEGER` | `60` | Stroke opacity from 0 through 255. |
| `--delay-ms INTEGER` | `20` | Delay between animated segments, in milliseconds. |
| `--fast` | Off | Render without the GUI; requires both `--input` and `--pegs`. |
| `-f/--force` | Off | Replace the exact output path without prompting. |
| `--help`, `-h` | — | Show command options and exit. |
| `--version` | — | Show the installed package version and exit. |

## Contributing

If you'd like to contribute, please follow these guidelines:

1. Fork the repository.
2. Create a new branch.
3. Make your changes and commit them.
4. Push to your fork and submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE) - see the [LICENSE](LICENSE) file for details.
