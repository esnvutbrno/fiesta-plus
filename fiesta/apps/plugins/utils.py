from apps.plugins.plugin import PluginAppConfig


def all_plugins_as_choices() -> list[tuple[str, str]]:
    return [(a.label, a.verbose_name) for a in all_plugin_apps()]


def all_plugin_apps() -> tuple["PluginAppConfig", ...]:
    """Returns all django app configs considered as PluginApps -- inheriting from PluginAppConfig."""
    from django.apps import apps

    return tuple(
        filter(lambda a: isinstance(a, PluginAppConfig), apps.get_app_configs())
    )
