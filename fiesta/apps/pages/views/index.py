from __future__ import annotations

from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin


class SinglePageView(EnsureInSectionSpaceViewMixin, DetailView):
    template_name = "pages/page.html"

    def get_queryset(self):
        return self.request.in_space_of_section.pages.filter(parent__isnull=True)


class DefaultPageView(EnsureInSectionSpaceViewMixin, DetailView):
    template_name = "pages/page.html"

    def get_object(self, queryset=None):
        return get_object_or_404(self.request.in_space_of_section.pages.filter(parent__isnull=True, default=True))
