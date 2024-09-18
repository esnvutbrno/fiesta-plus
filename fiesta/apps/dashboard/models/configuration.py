from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from apps.plugins.models import BasePluginConfiguration


class DashboardConfiguration(BasePluginConfiguration):

    class Meta:
        verbose_name = _("dashboard configuration")
        verbose_name_plural = _("dashboard configurations")


__all__ = ["DashboardConfiguration"]
