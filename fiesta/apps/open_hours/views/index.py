from __future__ import annotations

from django.http import Http404
from django.views.generic import TemplateView

from apps.plugins.views import PluginConfigurationViewMixin


class OpenHoursIndexView(TemplateView):
    template_name = "open_hours/index.html"


class MapView(
    PluginConfigurationViewMixin,
    TemplateView,
):
    template_name = "open_hours/map.html"

    def get(self, request, *args, **kwargs):
        if not self.configuration.show_map:
            raise Http404("Map is not enabled")

        return super().get(request, *args, **kwargs)
