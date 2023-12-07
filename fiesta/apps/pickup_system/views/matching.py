from __future__ import annotations

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView

from apps.fiestarequests.models.request import BaseRequestProtocol
from apps.fiestarequests.views.matching import BaseTakeRequestView
from apps.pickup_system.forms import PickupRequestMatchForm
from apps.pickup_system.models import PickupRequest, PickupRequestMatch, PickupSystemConfiguration
from apps.pickup_system.models.files import BaseIssuerPictureServeView, BaseMatcherPictureServeView
from apps.plugins.middleware.plugin import HttpRequest
from apps.plugins.views import PluginConfigurationViewMixin
from apps.sections.views.mixins.membership import EnsureLocalUserViewMixin
from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin
from apps.utils.breadcrumbs import with_breadcrumb, with_plugin_home_breadcrumb


@with_plugin_home_breadcrumb
@with_breadcrumb(_("Waiting Requests"))
class MatchingRequestsView(
    EnsureInSectionSpaceViewMixin,
    EnsureLocalUserViewMixin,
    PluginConfigurationViewMixin[PickupSystemConfiguration],
    ListView,
):
    template_name = "pickup_system/matching_requests.html"

    model = PickupRequest

    def get_queryset(self):
        return self.request.in_space_of_section.pickup_system_requests.filter(
            state=PickupRequest.State.CREATED,
        )


class MatchPickupRequestFormView(
    BaseTakeRequestView,
):
    match_model = PickupRequestMatch
    form_class = PickupRequestMatchForm

    form_url = "pickup_system:match-pickup-request"
    success_url = reverse_lazy("pickup_system:my-pickups")
    buddy_request: PickupRequest

    def get_queryset(self):
        return self.request.in_space_of_section.pickup_system_requests.filter(
            state=BaseRequestProtocol.State.CREATED,
        )


class ServeFilesFromPickupsMixin:
    @classmethod
    def get_request_queryset(cls, request: HttpRequest):
        return request.membership.section.pickup_system_requests


class IssuerPictureServeView(ServeFilesFromPickupsMixin, BaseIssuerPictureServeView):
    ...


class MatcherPictureServeView(
    ServeFilesFromPickupsMixin,
    BaseMatcherPictureServeView,
):
    ...
