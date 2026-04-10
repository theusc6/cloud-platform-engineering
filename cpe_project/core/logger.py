"""Structured logging configuration for CPE scripts."""

import logging
import sys


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Return a logger with a consistent format across all CPE scripts.

    Uses a StreamHandler writing to stdout so output works in terminals,
    CI runners, and CloudWatch Logs alike.
    """
    logger = logging.getLogger(f"cpe.{name}")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger
