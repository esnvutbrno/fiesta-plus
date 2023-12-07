from __future__ import annotations

from functools import lru_cache
from operator import attrgetter

from django.urls import ResolverMatch

from apps.plugins.plugin import BasePluginAppConfig


@lru_cache
def all_plugin_apps() -> tuple[BasePluginAppConfig, ...]:
    """Returns all django app configs considered as PluginApps -- inheriting from PluginAppConfig."""
    from django.apps import apps

    return tuple(
        sorted(
            filter(lambda a: isinstance(a, BasePluginAppConfig), apps.get_app_configs()), key=attrgetter("verbose_name")
        )
    )


@lru_cache
def all_plugins_as_choices() -> list[tuple[str, str]]:
    return [(a.label, a.verbose_name) for a in all_plugin_apps()]


@lru_cache
def all_plugins_mapped_to_label() -> dict[str, BasePluginAppConfig]:
    return {a.label: a for a in all_plugin_apps()}


@lru_cache
def all_plugins_to_order() -> dict[str, int]:
    return {a.label: a.order for a in all_plugin_apps()}


@lru_cache
def all_plugins_mapped_to_class() -> dict[type[BasePluginAppConfig], BasePluginAppConfig]:
    return {a.__class__: a for a in all_plugin_apps()}


def target_plugin_app_from_resolver_match(
    match: ResolverMatch,
) -> BasePluginAppConfig | None:
    if not match or not match.app_name:
        # no app --> cannot resolve plugin
        return None

    # TODO: resolver.app_name is full-dotted path
    # Plugin.app_label is just ending section
    # is there a cleaner way?
    target_app = match.app_name.split(".")[-1]

    return all_plugins_mapped_to_label().get(target_app)
