from __future__ import annotations

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView

from apps.buddy_system.models import BuddyRequest, BuddyRequestMatch, BuddySystemConfiguration
from apps.fiestarequests.views.matching import BaseTakeRequestView
from apps.pickup_system.models.files import BaseIssuerPictureServeView, BaseMatcherPictureServeView
from apps.pickup_system.views.matching import ServeFilesFromPickupsMixin
from apps.plugins.views import PluginConfigurationViewMixin
from apps.sections.views.mixins.membership import EnsureLocalUserViewMixin
from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin


class MatchingRequestsView(
    EnsureInSectionSpaceViewMixin,
    EnsureLocalUserViewMixin,
    PermissionRequiredMixin,
    PluginConfigurationViewMixin[BuddySystemConfiguration],
    ListView,
):
    template_name = "buddy_system/matching_requests.html"

    model = BuddyRequest

    def has_permission(self):
        return self.configuration.matching_policy_instance.can_member_match

    def get_queryset(self):
        return self.configuration.matching_policy_instance.limit_requests(
            qs=BuddyRequest.objects.get_queryset(),
            membership=self.request.membership,
        )


class TakeBuddyRequestView(
    PluginConfigurationViewMixin[BuddySystemConfiguration],
    PermissionRequiredMixin,
    BaseTakeRequestView,
):
    match_model = BuddyRequestMatch

    def has_permission(self):
        return self.configuration.matching_policy_instance.can_member_match

    def get_queryset(self):
        return self.configuration.matching_policy_instance.limit_requests(
            qs=BuddyRequest.objects.get_queryset(),
            membership=self.request.membership,
        )


class IssuerPictureServeView(ServeFilesFromPickupsMixin, BaseIssuerPictureServeView):
    ...


class MatcherPictureServeView(
    ServeFilesFromPickupsMixin,
    BaseMatcherPictureServeView,
):
    ...
