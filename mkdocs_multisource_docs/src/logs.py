"""
Root logger configuration
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_root_logger(
    level: int = logging.INFO,
    log_file: Path | None = None,
    fmt: str = "%(asctime)s [%(name)s] %(levelname)-8s %(message)s",
    datefmt: str = "%Y-%m-%d %H:%M:%S"
) -> None:
    """Configures the root logger for the entire project.

    Args:
        level: Logging level (default: logging.INFO).
        log_file: Path to log file (if None, logs only to console).
        fmt: Message format string.
        datefmt: Date format string.
    """
    # Remove any existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Configure handlers
    handlers = [console_handler]
    if log_file:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB per file
            backupCount=5               # Keep 5 backup copies
        )
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    # Apply basic configuration
    logging.basicConfig(level=level, handlers=handlers)

    # Silence noisy libraries
    # logging.getLogger("<libname>").setLevel(logging.WARNING)
