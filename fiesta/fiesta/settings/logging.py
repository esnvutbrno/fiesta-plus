from __future__ import annotations

from configurations.values import SecretValue, Value


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


class SentryConfigMixin:
    SENTRY_DSN: str = SecretValue(environ_required=False)

    @classmethod
    def post_setup(cls):
        super().post_setup()

        import sentry_sdk

        if cls.SENTRY_DSN:
            sentry_sdk.init(
                dsn=cls.SENTRY_DSN,
                # Set traces_sample_rate to 1.0 to capture 100%
                # of transactions for performance monitoring.
                traces_sample_rate=1.0,
                # Set profiles_sample_rate to 1.0 to profile 100%
                # of sampled transactions.
                # We recommend adjusting this value in production.
                profiles_sample_rate=1.0,
            )
