from __future__ import annotations

from django.views.generic import TemplateView

from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin


class PagesIndexView(EnsureInSectionSpaceViewMixin, TemplateView):
    template_name = "pages/index.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, page=self.request.in_space_of_section.pages.first())
