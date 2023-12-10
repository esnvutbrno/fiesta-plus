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
    RELEASE_NAME: str
    ENVIRONMENT_NAME: str  # from base
    SENTRY_JS_LOADER_URL = SecretValue(environ_required=False)
    SENTRY_DSN: str = SecretValue(environ_required=False)

    @classmethod
    def post_setup(cls):
        super().post_setup()

        import sentry_sdk

        if cls.SENTRY_DSN:
            sentry_sdk.init(
                dsn=cls.SENTRY_DSN,
                # sample only 10% of events to reduce incoming data
                traces_sample_rate=0.1,
                profiles_sample_rate=0.1,
                environment=cls.ENVIRONMENT_NAME,
                release=cls.RELEASE_NAME,
                enable_tracing=True,
            )
