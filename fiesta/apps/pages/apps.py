from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from apps.plugins.plugin import PluginAppConfig


class PagesConfig(PluginAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.pages"
    title = _("pages")

    configuration_model = "pages.PagesConfiguration"


__all__ = ["PagesConfig"]
