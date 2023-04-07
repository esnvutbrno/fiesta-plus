from __future__ import annotations

import typing
from functools import lru_cache

from django.urls import ResolverMatch

from apps.plugins.plugin import PluginAppConfig


@lru_cache
def all_plugin_apps() -> tuple["PluginAppConfig", ...]:
    """Returns all django app configs considered as PluginApps -- inheriting from PluginAppConfig."""
    from django.apps import apps

    return tuple(
        filter(lambda a: isinstance(a, PluginAppConfig), apps.get_app_configs())
    )


@lru_cache
def all_plugins_as_choices() -> list[tuple[str, str]]:
    return [(a.label, a.verbose_name) for a in all_plugin_apps()]


@lru_cache
def all_plugins_as_mapping() -> dict[str, "PluginAppConfig"]:
    return {a.label: a for a in all_plugin_apps()}


@lru_cache
def all_plugins_mapped_to_class() -> (
    dict[typing.Type["PluginAppConfig"], "PluginAppConfig"]
):
    return {a.__class__: a for a in all_plugin_apps()}


def target_plugin_app_from_resolver_match(
    match: ResolverMatch,
) -> PluginAppConfig | None:
    if not match or not match.app_name:
        # no app --> cannot resolve plugin
        return

    # TODO: resolver.app_name is full-dotted path
    # Plugin.app_label is just ending section
    # is there a cleaner way?
    target_app = match.app_name.split(".")[-1]

    return all_plugins_as_mapping().get(target_app)
