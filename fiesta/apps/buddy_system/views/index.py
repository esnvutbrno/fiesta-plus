from __future__ import annotations

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView

from apps.buddy_system.models import BuddyRequest, BuddySystemConfiguration
from apps.plugins.views import PluginConfigurationViewMixin
from apps.sections.middleware.user_membership import HttpRequest
from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin


class BuddySystemIndexView(
    EnsureInSectionSpaceViewMixin,
    PluginConfigurationViewMixin[BuddySystemConfiguration],
    TemplateView,
):
    request: HttpRequest

    extra_context = {
        "RequestState": BuddyRequest.State,
    }

    def get(self, request, *args, **kwargs):
        if (
            self.request.membership.is_international
            and not self.request.in_space_of_section.buddy_system_requests.filter(issuer=self.request.user).exists()
        ):
            return HttpResponseRedirect(reverse("buddy_system:wanna-buddy"))

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        data.update(
            {"requests": self.request.in_space_of_section.buddy_system_requests.filter(issuer=self.request.user)}
        )
        return data

    def get_template_names(self):
        return [
            (
                "buddy_system/index_international.html"
                if self.request.membership.is_international
                else "buddy_system/index_member.html"
            )
        ]
