
"""Logging configuration for Netaudit."""

import logging
import os
from pathlib import Path


def configure_logging(base_dir, verbose=False):

    log_dir = Path(base_dir) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("netaudit")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File logging
    file_handler = logging.FileHandler(
        log_dir / "netaudit.log",
        encoding="utf-8"
    )

    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Console logging
    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    level_name = os.getenv(
        "NETAUDIT_LOG_LEVEL", "ERROR"
    ).upper()

    if level_name not in levels:
        raise ValueError(
            f"Invalid logging level: {level_name}"
        )

    console_handler = logging.StreamHandler()

    if verbose:
        console_handler.setLevel(logging.DEBUG)
    else:
        console_handler.setLevel(levels[level_name])

    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
