from __future__ import annotations
from django.views.generic import TemplateView


class OpenHoursIndexView(TemplateView):
    template_name = "open_hours/index.html"


class MapView(TemplateView):
    template_name = "open_hours/map.html"
