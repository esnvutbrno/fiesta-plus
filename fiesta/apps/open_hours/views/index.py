from __future__ import annotations

import itertools

from django.http import Http404
from django.views.generic import TemplateView

from apps.plugins.views import PluginConfigurationViewMixin
from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin


class OpenHoursIndexView(EnsureInSectionSpaceViewMixin, TemplateView):
    template_name = "open_hours/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        groups = itertools.groupby(
            self.request.in_space_of_section.open_hours.all(),
            lambda x: x.day_index,
        )

        context["open_hours"] = [(day_index, list(group)) for day_index, group in groups]
        return context


class MapView(
    PluginConfigurationViewMixin,
    TemplateView,
):
    template_name = "open_hours/map.html"

    def get(self, request, *args, **kwargs):
        if not self.configuration.show_map:
            raise Http404("Map is not enabled")

        return super().get(request, *args, **kwargs)
