from __future__ import annotations

import typing

from django.utils.translation import gettext_lazy as _

from apps.plugins.plugin import PluginAppConfig

if typing.TYPE_CHECKING:
    from apps.plugins.middleware.plugin import HttpRequest
    from apps.utils.templatetags.navigation import NavigationItemSpec


class PagesConfig(PluginAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.pages"
    title = _("pages")

    configuration_model = "pages.PagesConfiguration"

    # login not required by default
    login_required = False

    @property
    def url_prefix(self) -> str:
        return "_/"

    def as_navigation_item(self, request: HttpRequest) -> NavigationItemSpec | None:
        return None


__all__ = ["PagesConfig"]
