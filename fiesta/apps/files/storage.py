from __future__ import annotations

import hashlib
import pathlib
import typing
from collections.abc import Callable
from urllib.parse import urljoin

from django.conf import settings
from django.core.files.storage import FileSystemStorage, Storage
from django.urls import reverse
from django.utils.encoding import filepath_to_uri
from django.utils.module_loading import import_string
from django.utils.timezone import now

if typing.TYPE_CHECKING:
    from apps.sections.middleware.section_space import HttpRequest
    from apps.utils.models import BaseModel

DEFAULT_STORAGE_CLASS: type[Storage] = import_string(settings.STORAGES["default"]["BACKEND"])


class NamespacedFilesStorage(DEFAULT_STORAGE_CLASS):
    """Django file storage, but supports namespaces and perms check (with cooperation with NamespacedFilesServeView)."""

    storages = []

    location: str

    def __init__(
        self,
        location: str,
        *,
        has_permission: Callable[[HttpRequest, str], bool] = (lambda *_: False),
    ):
        self.location = location.strip("/")

        # magics for S3/FS compatible class
        if issubclass(DEFAULT_STORAGE_CLASS, FileSystemStorage):
            location = settings.MEDIA_ROOT / self.location

        super().__init__(location=location)

        self.has_permission = has_permission

        self.storages.append(self)

    @property
    def url_name_suffix(self):
        return f"serve-{self.location}"

    def url(self, name):
        """Application public URL."""
        return reverse(f"files:{self.url_name_suffix}", kwargs=dict(name=filepath_to_uri(name)))

    def internal_serve_url(self, name):
        """Inner URL for serving internally by webserver."""
        return urljoin(settings.MEDIA_URL, f"{self.location}/{filepath_to_uri(name)}")

    @staticmethod
    def upload_to(instance: BaseModel, filename: str) -> str:
        ext = pathlib.Path(filename).suffix
        try:
            # for BaseTimestampedModel
            modified = instance.modified.isoformat()
        except AttributeError:
            modified = now().isoformat()

        return (
            pathlib.Path(
                hashlib.sha256(f"{instance.pk}-{modified}".encode()).hexdigest(),
            )
            .with_suffix(ext)
            .as_posix()
        )
