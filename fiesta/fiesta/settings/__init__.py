from __future__ import annotations

from configurations import Configuration
from configurations.values import DatabaseURLValue, Value

from .admin import AdminConfigMixin
from .auth import AuthConfigMixin
from .db import DatabaseConfigMixin
from .files import FilesConfigMixin, S3ConfigMixin
from .logging import LoggingConfigMixin
from .project import ProjectConfigMixin
from .security import SecurityConfigMixin
from .templates import TemplatesConfigMixin


class Base(
    ProjectConfigMixin,
    AuthConfigMixin,
    DatabaseConfigMixin,
    FilesConfigMixin,
    S3ConfigMixin,
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

    ROOT_DOMAIN = "fiesta.test"

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


class Production(Base):
    DEBUG = False

    ROOT_DOMAIN = Value(environ_required=True)

    DATABASES = DatabaseURLValue(environ_prefix="DJANGO")

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
