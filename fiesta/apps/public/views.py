from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from apps.plugins.middleware.plugin import HttpRequest
from apps.sections.middleware import UserMembershipMiddleware
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

        membership = self.request.membership

        home_url = self.request.in_space_of_section.section_home_url(membership)

        if membership and home_url:
            # home page for user with membership (we don't want to go to /pages/ from here)
            return HttpResponseRedirect(home_url)

        if self.request.user.is_authenticated:
            # we're on /, but user is logged in,
            # but we do not have home url, but user is logged in
            if membership:
                # doesn't have a membership, but the section is kinda misconfigured
                messages.warning(self.request, _("No home url configured for your section."))
            return UserMembershipMiddleware.handle_redirect_to_membership_select(
                request=self.request,
                membership=membership,
                with_warning=False,
            )

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
