import logging
import logging.config
import sys
from pathlib import Path

LOGS_DIR = Path("../logs")
LOGS_DIR.mkdir(exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "default",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "app.log",
            "maxBytes": 1024 * 1024,  # 1 MB
            "backupCount": 5,
            "formatter": "detailed",
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "error.log",
            "maxBytes": 1024 * 1024,
            "backupCount": 5,
            "formatter": "detailed",
            "level": "ERROR"
        }
    },
    "loggers": {
        "my_fastapi_app": {
            "handlers": ["console", "file", "error_file"],
            "level": "INFO",
            "propagate": False
        },
        "uvicorn": {
            "handlers": ["console", "file", "error_file"],
            "level": "INFO",
            "propagate": False
        },
        "uvicorn.error": {
            "handlers": ["console", "file", "error_file"],
            "level": "INFO",
            "propagate": False
        },
        "uvicorn.access": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False
        }
    },
    "root": {
        "handlers": ["console", "file", "error_file"],
        "level": "INFO",
    }
}

def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)

setup_logging()

logger = logging.getLogger("my_fastapi_app")