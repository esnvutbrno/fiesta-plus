from __future__ import annotations

from django.apps import AppConfig


class PluginsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.plugins"


__all__ = ["PluginsConfig"]
