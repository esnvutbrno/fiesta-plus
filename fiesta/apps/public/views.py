from __future__ import annotations

from django.views.generic import TemplateView

from apps.sections.views.mixins.section_space import EnsureNotInSectionSpaceViewMixin


class PublicHomepageView(EnsureNotInSectionSpaceViewMixin, TemplateView):
    template_name = "public/pages/public.html"

    def get_redirect_url(self):
        return self.request.in_space_of_section.section_home_url(self.request.membership) or super().get_redirect_url()


class PublicTeamView(EnsureNotInSectionSpaceViewMixin, TemplateView):
    template_name = "public/pages/team.html"
