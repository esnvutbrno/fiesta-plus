from __future__ import annotations

import typing

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.plugins.plugin import BasePluginAppConfig
from apps.utils.templatetags.navigation import NavigationItemSpec

if typing.TYPE_CHECKING:
    from apps.open_hours.models import OpenHoursConfiguration
    from apps.plugins.middleware.plugin import HttpRequest
    from apps.plugins.models.plugin import Plugin


class OpenHoursConfig(BasePluginAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.open_hours"
    verbose_name = _("Open Hours")
    emoji = "🕑"
    description = _("Open Hours shows the open hours of your office place.")

    configuration_model = "open_hours.OpenHoursConfiguration"

    def as_navigation_item(self, request: HttpRequest, bound_plugin: Plugin) -> NavigationItemSpec | None:
        base = super().as_navigation_item(request, bound_plugin)
        cfg: OpenHoursConfiguration = bound_plugin.configuration

        if not cfg.show_map:
            return base

        return base._replace(
            # url="",
            children=[
                NavigationItemSpec(title=_("Map"), url=reverse("open_hours:map")),
            ],
        )


__all__ = ["OpenHoursConfig"]
