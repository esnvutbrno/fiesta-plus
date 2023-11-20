from __future__ import annotations

import typing

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.plugins.plugin import BasePluginAppConfig
from apps.utils.templatetags.navigation import NavigationItemSpec

if typing.TYPE_CHECKING:
    from apps.plugins.middleware.plugin import HttpRequest
    from apps.plugins.models import Plugin


class BuddySystemConfig(BasePluginAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.buddy_system"
    verbose_name = _("Buddy System")
    emoji = "🤼"
    description = _("Tool for matching buddies with internationals.")
    order = 20

    configuration_model = "buddy_system.BuddySystemConfiguration"

    login_not_required_urls = (
        "wanna-buddy",
        "sign-up-before-request",
    )

    membership_not_required_urls = ("new-request",)

    def as_navigation_item(self, request: HttpRequest, bound_plugin: Plugin) -> NavigationItemSpec | None:
        base = (
            super()
            .as_navigation_item(request, bound_plugin)
            ._replace(
                children=(
                    [
                        NavigationItemSpec(title=_("My Buddies"), url=reverse("buddy_system:my-buddies")),
                    ]
                    if request.membership.is_local
                    else []
                ),
            )
        )

        if not request.membership.is_privileged:
            return base

        return base._replace(
            children=base.children
            + [
                NavigationItemSpec(title=_("Requests"), url=reverse("buddy_system:requests")),
            ],
        )


__all__ = ["BuddySystemConfig"]
