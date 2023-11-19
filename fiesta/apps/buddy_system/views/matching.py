from __future__ import annotations

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView

from apps.buddy_system.forms import BuddyRequestMatchForm
from apps.buddy_system.models import BuddyRequest, BuddyRequestMatch, BuddySystemConfiguration
from apps.fiestarequests.views.matching import BaseTakeRequestView
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


class MatchBuddyRequestFormView(
    PermissionRequiredMixin,
    BaseTakeRequestView,
):
    match_model = BuddyRequestMatch
    form_class = BuddyRequestMatchForm

    form_url = "buddy_system:match-buddy-request"
    success_url = reverse_lazy("buddy_system:my-buddies")
    buddy_request: BuddyRequest

    def has_permission(self):
        return self.configuration.matching_policy_instance.can_member_match

    def get_queryset(self):
        return self.configuration.matching_policy_instance.limit_requests(
            qs=BuddyRequest.objects.get_queryset(),
            membership=self.request.membership,
        )


class ServeFilesFromBuddiesMixin:
    @classmethod
    def get_request_queryset(cls, request: HttpRequest):
        return request.membership.section.buddy_system_requests


class IssuerPictureServeView(ServeFilesFromBuddiesMixin, BaseIssuerPictureServeView):
    ...


class MatcherPictureServeView(
    ServeFilesFromBuddiesMixin,
    BaseMatcherPictureServeView,
):
    ...
