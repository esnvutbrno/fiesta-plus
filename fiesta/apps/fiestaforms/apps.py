from __future__ import annotations

from django.apps import AppConfig
from django.forms import ClearableFileInput


class FiestaFormsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.fiestaforms"

    def ready(self):
        # would be so painful to ovverride them on all places
        ClearableFileInput.initial_text = "📁"
        ClearableFileInput.clear_checkbox_label = "clear file"
