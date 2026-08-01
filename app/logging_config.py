from __future__ import annotations

import logging
from typing import TextIO

from app.config import VALID_LOG_LEVELS

LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

APPLICATION_HANDLER_NAME = (
    "autodrive-kb-rag-console"
)

def configure_logging(log_level: str, stream: TextIO |None = None,)->None:
    """
    Configure application logging.

    Repeated calls replace the application-owned console handler
    instead of adding duplicate handlers.
    """
    if not isinstance(log_level, str):
        raise TypeError("log_level must be a string")
    
    normalized_level = log_level.strip().upper()

    if normalized_level not in VALID_LOG_LEVELS:
        raise ValueError("log_level must be one of: "
        "DEBUG, INFO, WARNING, ERROR, CRITICAL")
    
    numeric_level = getattr(logging, normalized_level)

    root_logger = logging.getLogger()

    for handler in list(root_logger.handlers):
        if (handler.get_name() == APPLICATION_HANDLER_NAME):
            root_logger.removeHandler(handler)
            handler.close()

    console_handler = logging.StreamHandler(stream)

    console_handler.set_name(APPLICATION_HANDLER_NAME)

    console_handler.setLevel(numeric_level)

    console_handler.setFormatter(
        logging.Formatter(
            fmt = LOG_FORMAT,
            datefmt = LOG_DATE_FORMAT,
        )
    )

    root_logger.addHandler(
        console_handler
    )

    root_logger.setLevel(
        numeric_level
    )