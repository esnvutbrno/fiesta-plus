from __future__ import annotations

import typing

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.plugins.plugin import PluginAppConfig
from apps.utils.templatetags.navigation import NavigationItemSpec

if typing.TYPE_CHECKING:
    from apps.plugins.middleware.plugin import HttpRequest


class ESNcardsConfig(PluginAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.esncards"

    configuration_model = "esncards.ESNcardsConfiguration"

    verbose_name = _("ESNcard")

    def as_navigation_item(self, request: HttpRequest) -> NavigationItemSpec | None:
        base = super().as_navigation_item(request)
        if not request.membership.is_privileged:
            return base

        return base._replace(
            url="",
            children=[
                NavigationItemSpec(title=_("Applications"), url=reverse("esncards:applications")),
            ],
        )


__all__ = ["ESNcardsConfig"]
