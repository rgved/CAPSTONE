"""
backend/services/logger.py

Provides a configured Logger instance for any module that requests one.

Usage:
    from backend.services.logger import get_logger
    logger = get_logger(__name__)
"""
import logging
import sys

from backend.config import LOG_LEVEL


def get_logger(name: str) -> logging.Logger:
    """
    Return a logger with the given name, configured to write to stdout.

    Loggers are cached by Python's logging module — calling this multiple
    times with the same name is safe and cheap.
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if the logger is fetched more than once.
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)-8s] %(name)s — %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False

    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)

    return logger
