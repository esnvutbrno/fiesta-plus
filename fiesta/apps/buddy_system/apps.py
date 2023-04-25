from __future__ import annotations

import typing

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.plugins.plugin import PluginAppConfig
from apps.utils.templatetags.navigation import NavigationItemSpec

if typing.TYPE_CHECKING:
    from apps.plugins.middleware.plugin import HttpRequest


class BuddySystemConfig(PluginAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.buddy_system"
    verbose_name = _("Buddy System")

    configuration_model = "buddy_system.BuddySystemConfiguration"

    login_not_required_urls = (
        "wanna-buddy",
        "sign-up-before-request",
    )

    membership_not_required_urls = ("new-request",)

    def as_navigation_item(self, request: HttpRequest) -> NavigationItemSpec | None:
        base = super().as_navigation_item(request)
        if not request.membership.is_privileged:
            return base

        return base._replace(
            url="",
            children=[
                NavigationItemSpec(title=_("Requests"), url=reverse("buddy_system:requests")),
            ],
        )


__all__ = ["BuddySystemConfig"]
