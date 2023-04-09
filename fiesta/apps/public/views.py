from __future__ import annotations

from django.views.generic import TemplateView

from apps.sections.views.mixins.section_space import EnsureNotInSectionSpaceViewMixin


class PublicHomepageView(EnsureNotInSectionSpaceViewMixin, TemplateView):
    template_name = "public/pages/public.html"


class PublicTeamView(EnsureNotInSectionSpaceViewMixin, TemplateView):
    template_name = "public/pages/team.html"
