from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from apps.plugins.plugin import PluginAppConfig


class DashboardConfig(PluginAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.dashboard"
    title = _("dashboard")

    configuration_model = "dashboard.DashboardConfiguration"


__all__ = ["DashboardConfig"]
