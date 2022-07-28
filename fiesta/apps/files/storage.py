import hashlib
import typing
from typing import Callable
from urllib.parse import urljoin

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from django.utils.encoding import filepath_to_uri
from django.utils.timezone import now

from apps.utils.models import BaseModel

if typing.TYPE_CHECKING:
    from apps.sections.middleware.section_space import HttpRequest


class NamespacedFilesStorage(FileSystemStorage):
    storages = []

    def __init__(
        self,
        namespace: str,
        *,
        has_permission: Callable[['HttpRequest', str], bool] = None
    ):
        self.namespace = namespace.strip("/")
        super().__init__(location=settings.MEDIA_ROOT / namespace)
        self.storages.append(self)
        self.has_permission = has_permission or (lambda *_: True)

    @property
    def url_name_suffix(self):
        return f"serve-{self.namespace}"

    def url(self, name):
        """Application public URL."""
        return reverse(
            f"files:{self.url_name_suffix}", kwargs=dict(name=filepath_to_uri(name))
        )

    def serve_url(self, name):
        """Inner URL for serving by webserver."""
        return urljoin(settings.MEDIA_URL, f"{self.namespace}/{filepath_to_uri(name)}")

    @staticmethod
    def upload_to(instance: BaseModel, filename: str) -> str:
        try:
            # for BaseTimestampedModel
            modified = instance.modified.isoformat()
        except AttributeError:
            modified = now().isoformat()

        return hashlib.sha256(f"{instance.pk}-{modified}".encode()).hexdigest()
