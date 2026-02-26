"""
BitHide Backend - Utility & Logging Layer
Centralized logger setup for all backend modules.
"""

import logging
import sys
import os
from logging.handlers import RotatingFileHandler


def get_logger(name: str, log_level: str = "INFO", log_file: str = "logs/bithide.log") -> logging.Logger:
    """
    Factory function to get a named logger with console + rotating file handlers.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # avoid adding duplicate handlers on reimport

    log_level_int = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(log_level_int)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level_int)
    logger.addHandler(console_handler)

    # Rotating File Handler (5MB per file, keep last 5)
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level_int)
    logger.addHandler(file_handler)

    return logger


# Root application-level logger
app_logger = get_logger("bithide", log_file="logs/bithide.log")
