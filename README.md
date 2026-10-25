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

Run `uv run picture-loom --help` to display the command options.

```sh
# Interactive image selection, cropping, peg selection, and animated drawing
uv run picture-loom

# Reproducible batch run: input, peg count, and line budget are explicit
uv run picture-loom --input img/sample1.png --pegs 22 --max-lines 5000 --fast

# Save to an exact path and overwrite that path without a prompt
uv run picture-loom -i img/sample1.png --pegs 22 --fast --output result.png --force
```

Options:

| Option | Default | Description |
| --- | --- | --- |
| `-i/--input IMAGE` | File chooser | Input image file; skips the file chooser. |
| `-o/--output PATH` | Content-addressed path | Exact PNG output path in fast mode. |
| `-v/--verbose` | INFO | One `-v` enables DEBUG logging. |
| `--crop/--no-crop` | Crop | Enable or skip cropping. |
| `--resize INTEGER` | `512` | Square output dimension. |
| `--pegs INTEGER` | Interactive selector | Number of pegs; omitted to select interactively. |
| `--max-lines INTEGER` | `5000` | Maximum number of drawn segments. |
| `--stroke-alpha INTEGER` | `60` | Stroke opacity from 0 through 255. |
| `--delay-ms INTEGER` | `20` | Delay between animated segments, in milliseconds. |
| `--fast` | Off | Render without the GUI; requires both `--input` and `--pegs`. |
| `-f/--force` | Off | Replace the exact output path without prompting. |

In fast mode, omitting `--output` writes to
`out/<sha256-of-final-PNG>.png` and creates `out/`. If the target exists, choose
`overwrite`, `numbered-duplicate`, or `cancel` (default). Numbered duplicates
use the number after the highest existing integer suffix, such as `image-8.png`
when `image-7.png` exists. At a collision with closed stdin, no file is changed;
use `--force` or choose a non-colliding `--output`.

`--output` is an exact file path. `--force` overwrites that exact path without
prompting. `--no-crop` skips cropping, but the pipeline still resizes the image
to a square.

## Contributing

If you'd like to contribute, please follow these guidelines:

1. Fork the repository.
2. Create a new branch.
3. Make your changes and commit them.
4. Push to your fork and submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE) - see the [LICENSE](LICENSE) file for details.
