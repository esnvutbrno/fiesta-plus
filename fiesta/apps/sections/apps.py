from apps.plugins.plugin import PluginAppConfig


class SectionsConfig(PluginAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.sections"

    configuration_model = "sections.SectionsConfiguration"


__all__ = ["SectionsConfig"]
