from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.plugins.models import BasePluginConfiguration


class ESNcardsConfiguration(BasePluginConfiguration):
    automatic_application_approving = models.BooleanField

    class Meta:
        verbose_name = _("esncards configuration")
        verbose_name_plural = _("esncards configurations")


__all__ = ["ESNcardsConfiguration"]
