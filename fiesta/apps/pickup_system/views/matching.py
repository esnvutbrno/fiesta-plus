from __future__ import annotations

from django.views.generic import ListView

from apps.fiestarequests.models.request import BaseRequestProtocol
from apps.fiestarequests.views.matching import BaseTakeRequestView
from apps.pickup_system.models import PickupRequest, PickupRequestMatch, PickupSystemConfiguration
from apps.pickup_system.models.files import BaseIssuerPictureServeView, BaseMatcherPictureServeView
from apps.plugins.middleware.plugin import HttpRequest
from apps.plugins.views import PluginConfigurationViewMixin
from apps.sections.views.mixins.membership import EnsureLocalUserViewMixin
from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin


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


class TakePickupRequestView(
    BaseTakeRequestView,
):
    match_model = PickupRequestMatch

    def get_queryset(self):
        return self.request.in_space_of_section.pickup_system_requests.filter(
            state=BaseRequestProtocol.State.CREATED,
        )


class ServeFilesFromPickupsMixin:
    def get_request_queryset(self, request: HttpRequest):
        return request.membership.section.pickup_system_requests


class IssuerPictureServeView(ServeFilesFromPickupsMixin, BaseIssuerPictureServeView):
    ...


class MatcherPictureServeView(
    ServeFilesFromPickupsMixin,
    BaseMatcherPictureServeView,
):
    ...
