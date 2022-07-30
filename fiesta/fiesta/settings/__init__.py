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
    USE_WEBPACK_INTEGRITY = False

    # https://stackoverflow.com/questions/1134290/cookies-on-localhost-with-explicit-domain
    SESSION_COOKIE_DOMAIN = None  # ".localhost"

    INTERNAL_IPS = type("ContainsAll", (), {"__contains__": lambda *_: True})()

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
