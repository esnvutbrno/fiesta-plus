from __future__ import annotations

from django.urls import reverse
from django.views.generic import RedirectView

from apps.accounts.templatetags.memberships import section_membership_activation_url
from apps.plugins.views import PluginConfigurationViewMixin
from apps.sections.models import SectionMembership
from apps.sections.views.mixins.section_space import EnsureNotInSectionSpaceViewMixin


class AfterLoginRedirectView(
    EnsureNotInSectionSpaceViewMixin,
    PluginConfigurationViewMixin,
    RedirectView,
):
    def get_redirect_url(self):
        active_memberships = self.request.all_memberships.filter(state=SectionMembership.State.ACTIVE)
        if active_memberships.count() == 1:
            m: SectionMembership = active_memberships.first()

            return section_membership_activation_url(dict(request=self.request), m)

        return reverse("accounts:membership")
