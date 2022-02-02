from apps.plugins.plugin import PluginAppConfig


class EsncardsConfig(PluginAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.esncards"

    configuration_model = "esncards.EsncardsConfiguration"


__all__ = ["EsncardsConfig"]
