import logging

from rich.logging import RichHandler


def init_logging(verbose: int = 0) -> None:
    """Initialize logging with RichHandler.

    Args:
        verbose: verbosity level (0 = INFO, >=1 = DEBUG)
    """
    level = logging.DEBUG if verbose else logging.INFO

    root = logging.getLogger()
    # If a RichHandler is already present, just update the level
    if any(isinstance(h, RichHandler) for h in root.handlers):
        root.setLevel(level)
        return

    rich_handler = RichHandler(rich_tracebacks=True)
    formatter = logging.Formatter("%(message)s")
    rich_handler.setFormatter(formatter)

    root.handlers = []
    root.addHandler(rich_handler)
    root.setLevel(level)
