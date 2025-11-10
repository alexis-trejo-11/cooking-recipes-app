import logging
import sys
from logging.config import dictConfig
import colorlog


def setup_logging():
    """Centralized logging configuration with colorized console output and file logging."""

    # Color Formatter
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s%(reset)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )

    # Color Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "colored_console": {
                "class": "logging.StreamHandler",
                "formatter": "colored",
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "logs/app.log",
                "maxBytes": 10485760,
                "backupCount": 3,
                "formatter": "detailed",
            },
        },
        "formatters": {
            "colored": {
                "()": "colorlog.ColoredFormatter",
                "format": "%(log_color)s%(asctime)s - %(name)-20s - %(levelname)-8s%(reset)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "log_colors": {
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bg_white",
                },
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "loggers": {
            "app": {
                "handlers": ["colored_console", "file"],
                "level": "INFO",
                "propagate": False,
            },
            "app.modules.recipe": {
                "handlers": ["colored_console", "file"],
                "level": "INFO",
                "propagate": False,
            },
            "app.modules.auth": {
                "handlers": ["colored_console", "file"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["colored_console"],
                "level": "INFO",
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "handlers": ["colored_console"],
                "level": "WARNING",
                "propagate": False,
            },
        },
        "root": {
            "handlers": ["colored_console"],
            "level": "INFO",
        },
    }

    dictConfig(LOGGING_CONFIG)
