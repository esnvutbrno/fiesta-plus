from __future__ import annotations

from django.apps import AppConfig

from apps.files._patches import monkeypatch_image_dimensions_caching


class FilesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.files"

    def ready(self):
        monkeypatch_image_dimensions_caching()
