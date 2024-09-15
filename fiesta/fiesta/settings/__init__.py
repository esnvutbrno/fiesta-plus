from __future__ import annotations

import dj_database_url
from configurations import Configuration
from configurations.values import SecretValue, Value

from .admin import AdminConfigMixin
from .auth import AuthConfigMixin
from .db import DatabaseConfigMixin
from .files import FilesConfigMixin, S3ConfigMixin
from .logging import LoggingConfigMixin, SentryConfigMixin
from .notifications import DatabaseSmtpMailerConfigMixin
from .project import ProjectConfigMixin
from .security import SecurityConfigMixin
from .templates import TemplatesConfigMixin


class Base(
    ProjectConfigMixin,
    AuthConfigMixin,
    DatabaseConfigMixin,
    FilesConfigMixin,
    LoggingConfigMixin,
    SecurityConfigMixin,
    TemplatesConfigMixin,
    AdminConfigMixin,
    Configuration,
):
    ...


class Development(Base):
    DEBUG = True
    DEBUG_PROPAGATE_EXCEPTIONS = False

    # no prefix since "ROOT_DOMAIN" is widely used
    ROOT_DOMAIN = Value(environ_prefix="")

    INTERNAL_IPS = type("ContainsAll", (), {"__contains__": lambda *_: True})()

    USE_WEBPACK_INTEGRITY = False

    def INSTALLED_APPS(self):
        return super().INSTALLED_APPS + ["debug_toolbar"]

    def MIDDLEWARE(self):
        middlewares = super().MIDDLEWARE
        middlewares.insert(1, "debug_toolbar.middleware.DebugToolbarMiddleware")
        return middlewares


class LocalProduction(Base):
    DEBUG = False

    ROOT_DOMAIN = "fiesta.test"

    USE_WEBPACK_INTEGRITY = False


class Production(
    DatabaseSmtpMailerConfigMixin,
    S3ConfigMixin,
    SentryConfigMixin,
    Base,
):
    DEBUG = False

    ROOT_DOMAIN = Value(environ_required=True)

    DATABASE_URL = SecretValue(environ_prefix="DJANGO")

    @property
    def DATABASES(self):
        return {
            "default": dj_database_url.parse(
                self.DATABASE_URL,
                conn_max_age=self.DATABASE_CONN_MAX_AGE,
                conn_health_checks=self.DATABASE_CONN_HEALTH_CHECKS,
            ),
            "wiki": DatabaseConfigMixin.DATABASES["wiki"],
        }

    ENVIRONMENT_NAME = Value(default="production")
    ENVIRONMENT_COLOR = Value(default="#7b3ff4")

    def STORAGES(self):
        return {
            "default": {
                "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            },
            "staticfiles": {
                # static files are not served by Django in production (only collected)
                "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
            },
        }

    @property
    def INSTALLED_APPS(self):
        return super().INSTALLED_APPS + ["health_check.contrib.s3boto3_storage"]
