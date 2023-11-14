from __future__ import annotations

from configurations.values import Value


class LoggingConfigMixin:
    LOG_LEVEL: str = Value("INFO")

    def LOGGING(self):
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "verbose": {
                    "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
                    "datefmt": "%d/%b/%Y %H:%M:%S",
                },
                "verbose.server": {
                    # TODO: [%(request)s] is bullshit here, since it's wsgi request only
                    #  try to find a way, how to include the domain
                    "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
                    "datefmt": "%d/%b/%Y %H:%M:%S",
                },
                "simple": {"format": "%(levelname)s %(message)s"},
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "verbose",
                },
                "console.server": {
                    "class": "logging.StreamHandler",
                    "formatter": "verbose.server",
                },
            },
            "root": {
                "handlers": ["console"],
                "level": "INFO",
            },
            "loggers": {
                "django": {
                    "handlers": ["console"],
                    "level": self.LOG_LEVEL,
                    "propagate": False,
                },
                "django.request": {
                    "handlers": ["console"],
                    "level": self.LOG_LEVEL,
                    "propagate": False,
                },
                "django.server": {
                    "handlers": ["console.server"],
                    "level": self.LOG_LEVEL,
                    "propagate": False,
                },
                "boto": {
                    "handlers": ["console"],
                    "level": self.LOG_LEVEL,
                },
            },
        }
