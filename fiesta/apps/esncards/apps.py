from django.utils.translation import gettext_lazy as _

from apps.plugins.plugin import PluginAppConfig


class ESNcardsConfig(PluginAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.esncards"

    configuration_model = "esncards.ESNcardsConfiguration"

    verbose_name = _("ESNcards")


__all__ = ["ESNcardsConfig"]
