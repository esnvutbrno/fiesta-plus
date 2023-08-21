from __future__ import annotations

import typing

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.plugins.plugin import BasePluginAppConfig
from apps.utils.templatetags.navigation import NavigationItemSpec

if typing.TYPE_CHECKING:
    from apps.plugins.middleware.plugin import HttpRequest
    from apps.plugins.models import Plugin


class ESNcardsConfig(BasePluginAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.esncards"
    verbose_name = _("ESNcard")
    emoji = "💳"
    description = _("ESNcard applications, processing and bulk export.")

    configuration_model = "esncards.ESNcardsConfiguration"

    def as_navigation_item(self, request: HttpRequest, bound_plugin: Plugin) -> NavigationItemSpec | None:
        base = super().as_navigation_item(request, bound_plugin)
        if not request.membership.is_privileged:
            return base

        return base._replace(
            url="",
            children=[
                NavigationItemSpec(title=_("Applications"), url=reverse("esncards:applications")),
                NavigationItemSpec(title=_("Exports"), url=reverse("esncards:exports")),
            ],
        )


__all__ = ["ESNcardsConfig"]
