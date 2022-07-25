from django.utils.translation import gettext_lazy as _

from apps.plugins.plugin import PluginAppConfig


class SectionsConfig(PluginAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.sections"

    configuration_model = "sections.SectionsConfiguration"

    verbose_name = _("ESN section")

    login_not_required_urls = [
        "choose-space",
    ]


__all__ = ["SectionsConfig"]
