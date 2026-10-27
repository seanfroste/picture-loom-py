"""Public package metadata and import namespace for Picture Loom."""

# picture_loom - Convert images into circular weaving loom patterns

try:
    from importlib.metadata import version

    __version__ = version("picture-loom")
except Exception:
    __version__ = "0.0.0-dev"
