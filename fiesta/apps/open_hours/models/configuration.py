from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.plugins.models import BasePluginConfiguration


class OpenHoursConfiguration(BasePluginConfiguration):
    show_map = models.BooleanField(
        verbose_name=_("show map on open hours page"),
        default=True,
    )

    class Meta:
        verbose_name = _("open hours configuration")
        verbose_name_plural = _("open hours configurations")


__all__ = ["OpenHoursConfiguration"]
