from __future__ import annotations

import hashlib
import pathlib
import typing
from collections.abc import Callable
from urllib.parse import urljoin

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from django.utils.encoding import filepath_to_uri
from django.utils.timezone import now

if typing.TYPE_CHECKING:
    from apps.sections.middleware.section_space import HttpRequest
    from apps.utils.models import BaseModel


class NamespacedFilesStorage(FileSystemStorage):
    """Django file storage, but supports namespaces and perms check (with cooperation with NamespacedFilesServeView)."""

    storages = []

    namespace: str

    def __init__(
        self,
        namespace: str,
        *,
        has_permission: Callable[[HttpRequest, str], bool] = (lambda *_: False),
    ):
        self.namespace = namespace.strip("/")
        super().__init__(location=settings.MEDIA_ROOT / namespace)
        self.has_permission = has_permission

        self.storages.append(self)

    @property
    def url_name_suffix(self):
        return f"serve-{self.namespace}"

    def url(self, name):
        """Application public URL."""
        return reverse(f"files:{self.url_name_suffix}", kwargs=dict(name=filepath_to_uri(name)))

    def internal_serve_url(self, name):
        """Inner URL for serving internally by webserver."""
        return urljoin(settings.MEDIA_URL, f"{self.namespace}/{filepath_to_uri(name)}")

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
