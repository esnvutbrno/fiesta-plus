from __future__ import annotations

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.http import urlencode
from django.views.generic import TemplateView

from apps.plugins.middleware.plugin import HttpRequest
from apps.sections.views.mixins.section_space import EnsureNotInSectionSpaceViewMixin


class RootPageView(
    TemplateView,
    # intentionally as second to have default dispatch, but access to non-section-space url
    EnsureNotInSectionSpaceViewMixin,
):
    """Serves content on / url, which is dynamic by logged/not logged user and in/out of section space."""

    request: HttpRequest

    template_name = "public/pages/public.html"

    def get(self, request, *args, **kwargs):
        if not self.request.in_space_of_section:
            return super().get(request, *args, **kwargs)

        home_url = self.request.in_space_of_section.section_home_url(self.request.membership)

        if home_url:
            return HttpResponseRedirect(home_url)

        return HttpResponseRedirect(
            reverse("account_login")
            + "?"
            + urlencode(
                {
                    **self.request.GET,
                    REDIRECT_FIELD_NAME: self.request.path,
                }
            )
        )


class PublicTeamView(EnsureNotInSectionSpaceViewMixin, TemplateView):
    template_name = "public/pages/team.html"
