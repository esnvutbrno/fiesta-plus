from __future__ import annotations

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView

from apps.pickup_system.models import PickupRequest, PickupSystemConfiguration
from apps.plugins.views import PluginConfigurationViewMixin
from apps.sections.middleware.user_membership import HttpRequest
from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin


class PickupSystemIndexView(
    EnsureInSectionSpaceViewMixin,
    PluginConfigurationViewMixin[PickupSystemConfiguration],
    TemplateView,
):
    request: HttpRequest

    extra_context = {
        "RequestState": PickupRequest.State,
    }

    def get(self, request, *args, **kwargs):
        if (
            self.request.membership.is_international
            and not self.request.in_space_of_section.pickup_system_requests.filter(issuer=self.request.user).exists()
        ):
            return HttpResponseRedirect(reverse("pickup_system:new-request"))

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        data.update(
            {"requests": self.request.in_space_of_section.pickup_system_requests.filter(issuer=self.request.user)}
        )
        return data

    def get_template_names(self):
        return [
            (
                "pickup_system/index_international.html"
                if self.request.membership.is_international
                else "pickup_system/index_member.html"
            )
        ]
