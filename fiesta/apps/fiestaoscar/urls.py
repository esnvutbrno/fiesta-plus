from __future__ import annotations

from django.apps import apps

# oscar from "oscar" (not fiestaoscar), because label is kept default as "oscar"
urlpatterns = apps.get_app_config("oscar").get_urls()
