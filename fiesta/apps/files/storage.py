from __future__ import annotations

import hashlib
import pathlib
import typing
from collections.abc import Callable
from urllib.parse import urljoin

import magic
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

USING_LOCAL_FS_STORAGE = issubclass(DEFAULT_STORAGE_CLASS, FileSystemStorage)


class NamespacedFilesStorage(DEFAULT_STORAGE_CLASS):
    """Django file storage, but supports namespaces and perms check (with cooperation with NamespacedFilesServeView)."""

    storages = []

    location: str
    namespace: str

    def __init__(
        self,
        namespace: str,
        *,
        has_permission: Callable[[HttpRequest, str], bool] = (lambda *_: False),
    ):
        self.namespace = location = namespace

        # magics for S3/FS compatible class
        if USING_LOCAL_FS_STORAGE:
            location = settings.MEDIA_ROOT / namespace

        super().__init__(location=location)

        self.has_permission = has_permission

        self.storages.append(self)

    def url(self, name):
        """Application public URL."""
        return reverse(f"files:serve-{self.location}", kwargs=dict(name=filepath_to_uri(name)))

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

    if USING_LOCAL_FS_STORAGE:
        mime = magic.Magic(mime=True)

        def object_response_headers(self, name: str) -> dict[str, str]:
            return {
                "Content-Disposition": f'filename="{name}"',
                "Content-Type": self.mime.from_file(self.path(name=name)),
                "X-Accel-Redirect": urljoin(settings.MEDIA_URL, f"{self.namespace}/{filepath_to_uri(name)}"),
            }

    else:

        def object_response_headers(self, name: str) -> dict[str, str]:
            return {
                "X-Accel-Redirect": "@s3",
                # TODO: think about defining public url of bucket directly to nginx proxypass conf
                "X-Accel-Redirect-Host": settings.S3_PUBLIC_URL,
                "X-Accel-Redirect-Path": f"{self.namespace}/{name}",
                # https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_buffering
                # waiting for a client is fine here, it's not blocking us but the S3
                "X-Accel-Buffering": "no",
            }
