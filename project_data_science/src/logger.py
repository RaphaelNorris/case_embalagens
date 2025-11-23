"""
Centralized logging configuration using loguru.
Provides structured logging with different formatters for development and production.
"""

import sys
from pathlib import Path

from loguru import logger

from .config import get_config

# Remove default logger
logger.remove()


def setup_logger():
    """
    Configure logger based on environment settings.

    In development: colored console output with detailed format
    In production: JSON format for structured logging
    """
    config = get_config()

    # Console handler
    if config.log_format == "json":
        # Production: JSON format
        logger.add(
            sys.stderr,
            format="{message}",
            level=config.log_level,
            serialize=True,
        )
    else:
        # Development: human-readable format with colors
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=config.log_level,
            colorize=True,
        )

    # File handler for all environments
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Rotating file handler
    logger.add(
        log_dir / "adami_{time:YYYY-MM-DD}.log",
        rotation="00:00",  # Rotate at midnight
        retention="30 days",  # Keep logs for 30 days
        compression="zip",  # Compress old logs
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=config.log_level,
        enqueue=True,  # Thread-safe
    )

    # Error file handler
    logger.add(
        log_dir / "errors_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="90 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        enqueue=True,
    )

    logger.info(f"Logger configured for {config.environment} environment")
    return logger


# Initialize logger
setup_logger()


def get_logger(name: str = None):
    """
    Get a logger instance with optional name binding.

    Args:
        name: Optional name to bind to the logger (usually __name__)

    Returns:
        Configured logger instance
    """
    if name:
        return logger.bind(name=name)
    return logger
