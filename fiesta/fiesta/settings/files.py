from pathlib import Path

from . import config, BaseConfigurationProtocol


class FilesConfigMixin(BaseConfigurationProtocol):
    STATIC_URL = "static/"

    STATIC_ROOT = config("STATIC_DIR", cast=Path)

    def STATICFILES_DIRS(self):
        return [
            (self.BASE_DIR / "static"),
            (self.BASE_DIR / "templates/static"),
        ]

    MEDIA_ROOT = config("MEDIA_DIR", cast=Path)

    # internal for nginx
    MEDIA_URL = "/media/"

    @property
    def WEBPACK_LOADER(self):
        return {
            "DEFAULT": {
                "CACHE": False,
                "BUNDLE_DIR_NAME": "./",  # must end with slash
                "STATS_FILE": config("BUILD_DIR", cast=Path) / "webpack-stats.json",
                "INTEGRITY": not self.DEBUG,
            }
        }
