# app/config/logging_config.py
import logging
import sys
from logging.config import dictConfig
from pathlib import Path
from app.config.app_settings import settings

_LOGGING_CONFIGURED = False


def setup_logging():
    """Centralized logging configuration - prevents multiple setup"""
    global _LOGGING_CONFIGURED

    if _LOGGING_CONFIGURED:
        return

    _LOGGING_CONFIGURED = True

    base_level = "DEBUG" if settings.DEBUG else "INFO"

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "colored": {
                "()": "colorlog.ColoredFormatter",
                "format": "%(log_color)s%(asctime)s - %(name)-25s - %(levelname)-8s%(reset)s - %(message)s",
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
        "handlers": {
            "colored_console": {
                "class": "logging.StreamHandler",
                "level": base_level,
                "formatter": "colored",
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "detailed",
                "filename": "logs/app.log",
                "maxBytes": 10485760,
                "backupCount": 3,
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "app": {
                "level": base_level,
                "handlers": ["colored_console", "file"],
                "propagate": False,
            },
            "app.modules.auth": {
                "level": base_level,
                "handlers": ["colored_console", "file"],
                "propagate": False,
            },
            "app.modules.recipe": {
                "level": base_level,
                "handlers": ["colored_console", "file"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["colored_console"],
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "level": "WARNING" if not settings.DEBUG else "INFO",
                "handlers": ["colored_console"],
                "propagate": False,
            },
            "watchfiles": {
                "level": "WARNING",
                "propagate": False,
            },
        },
        "root": {
            "level": "WARNING",
            "handlers": ["colored_console"],
        },
    }

    dictConfig(LOGGING_CONFIG)

    init_logger = logging.getLogger("app.config")
    init_logger.info(f"Logging configured - DEBUG: {settings.DEBUG}")
