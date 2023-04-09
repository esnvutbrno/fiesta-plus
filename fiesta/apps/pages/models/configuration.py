from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from apps.plugins.models import BasePluginConfiguration


class PagesConfiguration(BasePluginConfiguration):
    ...

    class Meta:
        verbose_name = _("pages configuration")
        verbose_name_plural = _("pages configurations")


__all__ = ["PagesConfiguration"]
