import magic
from django.http import HttpResponse, Http404
from django.urls import path
from django.urls.resolvers import RoutePattern
from django.views import View

from apps.files import logger
from apps.files.storage import NamespacedFilesStorage


class NamespacedFilesServeView(View):
    mime = magic.Magic(mime=True)

    storage: NamespacedFilesStorage = None
    namespace: str = None

    def get(self, request, name: str, *args, **kwargs) -> HttpResponse:
        if not self.storage.exists(name):
            logger.warning("File %s in namespace %s not found.", name, self.namespace)
            raise Http404()

        return HttpResponse(
            headers={
                "Content-Disposition": f'filename="{name}"',
                "X-Accel-Redirect": self.storage.serve_url(name),
                "Content-Type": self.mime.from_file(self.storage.path(name=name)),
            }
        )

    @classmethod
    def as_url(cls, storage: NamespacedFilesStorage) -> RoutePattern:
        return path(
            f"serve/{storage.namespace}/<path:name>",
            cls.as_view(
                storage=storage,
            ),
            name=f"serve-{storage.namespace}",
        )
