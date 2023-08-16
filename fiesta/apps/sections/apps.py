from __future__ import annotations

import typing

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.plugins.plugin import BasePluginAppConfig
from apps.utils.templatetags.navigation import NavigationItemSpec

if typing.TYPE_CHECKING:
    from apps.plugins.middleware.plugin import HttpRequest
    from apps.plugins.models import Plugin


class SectionsConfig(BasePluginAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.sections"
    verbose_name = _("ESN section")
    emoji = "🏡"
    description = _("Section management of members, statistics and Fiesta settings.")

    configuration_model = "sections.SectionsConfiguration"

    login_not_required_urls = [
        "choose-space",
    ]

    auto_enabled = True

    def as_navigation_item(self, request: HttpRequest, bound_plugin: Plugin) -> NavigationItemSpec | None:
        if not request.membership.is_privileged:
            # non privileged users should not see the plugin at all
            return None
        return (
            super()
            .as_navigation_item(request, bound_plugin)
            ._replace(
                url="",
                children=[
                    NavigationItemSpec(
                        _("Members"),
                        reverse("sections:section-members"),
                    ),
                    NavigationItemSpec(
                        _("Statistics"),
                        reverse("sections:section-stats"),
                    ),
                    NavigationItemSpec(
                        _("Settings"),
                        reverse("sections:section-settings"),
                    ),
                ],
            )
        )


__all__ = ["SectionsConfig"]
