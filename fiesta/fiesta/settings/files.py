from __future__ import annotations

from pathlib import Path

from ._utils import BaseConfigurationProtocol, PathValue


class FilesConfigMixin(BaseConfigurationProtocol):
    MEDIA_ROOT: Path = PathValue()

    STATIC_ROOT: Path = PathValue()

    BUILD_DIR: Path = PathValue()

    # internal for nginx
    MEDIA_URL = "/media/"
    STATIC_URL = "static/"

    def STATICFILES_DIRS(self):
        return [
            (self.BASE_DIR / "static"),
            (self.BASE_DIR / "templates/static"),
        ]

    def USE_WEBPACK_INTEGRITY(self):
        return not self.DEBUG

    @property
    def WEBPACK_LOADER(self):
        return {
            "DEFAULT": {
                "CACHE": False,
                "BUNDLE_DIR_NAME": "./",  # must end with slash
                "STATS_FILE": self.BUILD_DIR / "webpack-stats.json",
                "INTEGRITY": self.USE_WEBPACK_INTEGRITY,
            }
        }

    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

    PICTURES = {
        "USE_PLACEHOLDERS": False,
        "BREAKPOINTS": {
            # https://tailwindcss.com/docs/screens
            "sm": 640,
            "md": 768,
            "lg": 1024,
            "xl": 1280,
            "2xl": 1536,
        },
        "GRID_COLUMNS": 12,
        "CONTAINER_WIDTH": 1536,
        "FILE_TYPES": ["WEBP"],
        "PIXEL_DENSITIES": [1, 2],
        "QUEUE_NAME": None,
    }
