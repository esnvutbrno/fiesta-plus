from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from apps.plugins.plugin import BasePluginAppConfig


class OpenHoursConfig(BasePluginAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.open_hours"
    verbose_name = _("Open Hours")
    emoji = "🕑"
    description = _("Open Hours shows the open hours of your office place.")

    configuration_model = "open_hours.OpenHoursConfiguration"


__all__ = ["OpenHoursConfig"]
