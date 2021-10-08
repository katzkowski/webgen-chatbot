from datetime import datetime

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "basic": {"format": "%(name)s - %(levelname)s - %(message)s"},
        "extended": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "ERROR",
            "class": "logging.StreamHandler",
            "formatter": "basic",
            "stream": "ext://sys.stdout",
        },
        "console_test": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "extended",
            "stream": "ext://sys.stdout",
        },
        "file_handler": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "formatter": "extended",
            "filename": "./logs/{:%Y-%m-%d_%H-%M-%S}.log".format(datetime.now()),
        },
    },
    "loggers": {
        "db": {
            "level": "ERROR",
            "handlers": ["console", "file_handler"],
            "propagate": False,
        },
        "db_backup": {
            "level": "INFO",
            "handlers": ["console", "file_handler"],
            "propagate": False,
        },
        "schema": {
            "level": "ERROR",
            "handlers": ["console", "file_handler"],
            "propagate": False,
        },
        "crawler": {
            "level": "INFO",
            "handlers": ["console", "file_handler"],
            "propagate": False,
        },
        "downloader": {
            "level": "INFO",
            "handlers": ["console", "file_handler"],
            "propagate": False,
        },
        "dataset": {
            "level": "INFO",
            "handlers": ["console", "file_handler"],
            "propagate": False,
        },
        "training": {
            "level": "INFO",
            "handlers": ["console", "file_handler"],
            "propagate": False,
        },
        "cluster matcher": {
            "level": "INFO",
            "handlers": ["console", "file_handler"],
            "propagate": False,
        },
        "scraper": {
            "level": "INFO",
            "handlers": ["console", "file_handler"],
            "propagate": False,
        },
        "main": {
            "level": "INFO",
            "handlers": ["console", "file_handler"],
            "propagate": False,
        },
        "imggen": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console"],
    },
}
