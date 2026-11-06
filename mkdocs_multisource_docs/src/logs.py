"""Root logger configuration."""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

DEFAULT_FORMAT = "%(asctime)s [%(name)s] %(levelname)-8s %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class ColorFormatter(logging.Formatter):
    """Format log metadata with ANSI colors when writing to a terminal."""

    RESET = "\033[0m"
    DIM = "\033[2m"
    CYAN = "\033[36m"
    LEVEL_COLORS = {
        logging.DEBUG: "\033[34m",
        logging.INFO: "\033[32m",
        logging.WARNING: "\033[33m",
        logging.ERROR: "\033[31m",
        logging.CRITICAL: "\033[1;31m",
    }

    def __init__(
        self,
        *,
        datefmt: str = DEFAULT_DATE_FORMAT,
        use_color: bool | None = None,
    ) -> None:
        super().__init__(datefmt=datefmt)
        self.use_color = sys.stderr.isatty() if use_color is None else use_color

    def format(self, record: logging.LogRecord) -> str:
        timestamp = self.formatTime(record, self.datefmt)
        level = f"{record.levelname:<8}"
        message = record.getMessage()

        if record.exc_info:
            message = f"{message}\n{self.formatException(record.exc_info)}"
        if record.stack_info:
            message = f"{message}\n{self.formatStack(record.stack_info)}"

        if not self.use_color:
            return f"{timestamp} [{record.name}] {level} {message}"

        level_color = self.LEVEL_COLORS.get(record.levelno, self.RESET)
        return (
            f"{self.DIM}{timestamp}{self.RESET} "
            f"{self.CYAN}[{record.name}]{self.RESET} "
            f"{level_color}{level}{self.RESET} {message}"
        )


def setup_root_logger(
    level: int = logging.INFO,
    log_file: Path | None = None,
    fmt: str = DEFAULT_FORMAT,
    datefmt: str = DEFAULT_DATE_FORMAT,
) -> None:
    """Configure the root logger for the entire project."""
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColorFormatter(datefmt=datefmt))

    handlers: list[logging.Handler] = [console_handler]
    if log_file:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
        )
        file_handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))
        handlers.append(file_handler)

    logging.basicConfig(level=level, handlers=handlers)
