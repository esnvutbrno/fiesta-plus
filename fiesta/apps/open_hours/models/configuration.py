from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.files.storage import NamespacedFilesStorage
from apps.plugins.models import BasePluginConfiguration
from apps.sections.middleware.user_membership import HttpRequest


def has_perms_to_view_map(request: HttpRequest, name: str) -> bool:
    # TODO: check if the configuration allows the access to the map
    return True


map_storage = NamespacedFilesStorage(
    "open-hours-map",
    has_permission=has_perms_to_view_map,
)


class OpenHoursConfiguration(BasePluginConfiguration):
    show_map = models.BooleanField(
        verbose_name=_("show map on open hours page"),
        default=True,
    )

    map = models.ImageField(
        verbose_name=_("map"),
        upload_to=map_storage.upload_to,
        storage=map_storage,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("open hours configuration")
        verbose_name_plural = _("open hours configurations")


__all__ = ["OpenHoursConfiguration"]
