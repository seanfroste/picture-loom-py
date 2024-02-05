# Picture Loom

An algorithmic generator for making string art out of digital images

## Table of Contents

- [Picture Loom](#picture-loom)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Default](#default)
    - [`--no-crop`](#--no-crop)
  - [Contributing](#contributing)
  - [License](#license)

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/seanfroste/picture-loom-py.git
    ```

2. Navigate to the project directory:

    ```sh
    cd picture-loom-py
    ```

3. (Optional) Create and activate a virtual environment:

    - On Linux/Mac

        ```sh
        python -m venv venv
        source venv/bin/activate
        ```

    - On Windows

        ```powershell
        python.exe -m venv venv
        .\venv\Scripts\activate
        ```

4. Install dependencies:

    ```sh
    pip install -r requirements.txt
    ```

## Usage

### Default

Run main.py to initialize the program

```sh
python main.py
```

### `--no-crop`

The `--no-crop` flag applies a default 1:1 crop to the image, starting at the top left and of size that is the minimum of the image's width and height

```sh
python main.py --no-crop

```

## Contributing

If you'd like to contribute, please follow these guidelines:

1. Fork the repository.
2. Create a new branch.
3. Make your changes and commit them.
4. Push to your fork and submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE) - see the [LICENSE](LICENSE) file for details.
