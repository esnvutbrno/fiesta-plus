from __future__ import annotations

from django.apps import AppConfig


class UniversitiesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.universities"


__all__ = ["UniversitiesConfig"]
