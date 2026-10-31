import logging
from pathlib import Path
import os


def configure_logging(base_dir, verbose=False):

    log_dir = Path(base_dir) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("netaudit")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler = logging.FileHandler(
        log_dir / "netaudit.log",
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()

    log_level = os.getenv(
        "NETAUDIT_LOG_LEVEL", "ERROR"
    ).upper()

    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }

    if log_level not in levels:
        raise ValueError(
            f"Unsupported logging level: {log_level}"
        )

    console_handler = logging.StreamHandler()

    if verbose:
        console_handler.setLevel(logging.DEBUG)
    else:
        console_handler.setLevel(levels[log_level])

    console_handler.setFormatter(formatter)

    console_handler.setFormatter(formatter)

    # Avoid accumulating handlers if called more than once.
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger