from configurations import Configuration

from .auth import AuthConfigMixin
from .db import DatabaseConfigMixin
from .files import FilesConfigMixin
from .logging import LoggingConfigMixin
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


class Production(Base):
    DEBUG = False
