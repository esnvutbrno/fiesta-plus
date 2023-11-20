from __future__ import annotations

import typing

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.plugins.plugin import BasePluginAppConfig
from apps.utils.templatetags.navigation import NavigationItemSpec

if typing.TYPE_CHECKING:
    from apps.plugins.middleware.plugin import HttpRequest
    from apps.plugins.models import Plugin


class PickupSystemConfig(BasePluginAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.pickup_system"
    verbose_name = _("Pickup System")
    emoji = "🤼"
    description = _("Tools for managing pickup of your students.")
    feature_state = BasePluginAppConfig.FeatureState.EXPERIMENTAL
    order = 30

    configuration_model = "pickup_system.PickupSystemConfiguration"

    login_not_required_urls = (
        "wanna-pickup",
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
                        NavigationItemSpec(title=_("My Pickups"), url=reverse("pickup_system:my-pickups")),
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
                NavigationItemSpec(title=_("Requests"), url=reverse("pickup_system:requests")),
            ],
        )


__all__ = ["PickupSystemConfig"]
