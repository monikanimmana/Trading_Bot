"""
Logging configuration for the trading bot.
Sets up both file and console handlers with appropriate formatting.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Configure and return the root logger for the trading bot.

    Sets up:
    - A rotating file handler writing to logs/trading_bot_YYYYMMDD.log
    - A console (stderr) handler for INFO+ messages
    """
    os.makedirs(LOG_DIR, exist_ok=True)

    log_filename = os.path.join(
        LOG_DIR, f"trading_bot_{datetime.now().strftime('%Y%m%d')}.log"
    )

    # Root logger for the bot
    logger = logging.getLogger("trading_bot")
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers if setup_logging is called more than once
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # --- File handler (DEBUG and above, rotating, max 5 MB × 3 backups) ---
    file_handler = RotatingFileHandler(
        log_filename, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # --- Console handler (INFO and above) ---
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.debug("Logging initialised. Log file: %s", log_filename)
    return logger


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the 'trading_bot' namespace."""
    return logging.getLogger(f"trading_bot.{name}")
