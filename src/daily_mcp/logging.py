"""Logging configuration for daily-mcp."""

import logging
import sys
from pathlib import Path

# Default log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    level: int = logging.INFO,
    log_file: Path | None = None,
) -> logging.Logger:
    """
    Set up logging for the application.

    Args:
        level: Logging level (default: INFO)
        log_file: Optional path to log file

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("daily_mcp")
    logger.setLevel(level)

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler (stderr to not interfere with MCP stdio)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Optional name suffix for the logger

    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"daily_mcp.{name}")
    return logging.getLogger("daily_mcp")
