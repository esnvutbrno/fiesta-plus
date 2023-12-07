from __future__ import annotations

from pathlib import Path

from configurations.values import SecretValue

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
            # dir with wiki statics during debug
            # TODO: pass from env
            "/usr/src/wiki/static/",
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
            # "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }


class S3ConfigMixin(BaseConfigurationProtocol):
    AWS_S3_ACCESS_KEY_ID = SecretValue()
    AWS_S3_SECRET_ACCESS_KEY = SecretValue()
    AWS_STORAGE_BUCKET_NAME = SecretValue()
    AWS_S3_REGION_NAME = SecretValue()

    AWS_DEFAULT_ACL = "public-read"
    AWS_S3_SIGNATURE_VERSION = "s3v4"

    @property
    def AWS_S3_HOST(self):
        return f"s3.{self.AWS_S3_REGION_NAME}.scw.cloud"

    @property
    def AWS_S3_ENDPOINT_URL(self):
        return f"https://{self.AWS_S3_HOST}"

    @property
    def S3_PUBLIC_URL(self):
        """custom"""
        return f"{self.AWS_STORAGE_BUCKET_NAME}.{self.AWS_S3_HOST}"
