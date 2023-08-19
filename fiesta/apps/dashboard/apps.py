from __future__ import annotations

import typing

from django.utils.translation import gettext_lazy as _

from apps.plugins.plugin import PluginAppConfig
from apps.utils.templatetags.navigation import NavigationItemSpec

if typing.TYPE_CHECKING:
    from apps.plugins.middleware.plugin import HttpRequest
    from apps.plugins.models.plugin import Plugin


class DashboardConfig(PluginAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.dashboard"
    title = _("dashboard")
    emoji = "🧮"

    configuration_model = "dashboard.DashboardConfiguration"

    def as_navigation_item(self, request: HttpRequest, bound_plugin: Plugin) -> NavigationItemSpec | None:
        # do not display in menu, since it's the home button link if the plugin is enabled
        return None


__all__ = ["DashboardConfig"]
