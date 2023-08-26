from __future__ import annotations

import uuid

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils.translation import gettext as _
from django.views.generic import ListView
from django.views.generic.detail import BaseDetailView
from django_htmx.http import HttpResponseClientRedirect

from apps.buddy_system.models import BuddyRequest, BuddySystemConfiguration
from apps.files.views import NamespacedFilesServeView
from apps.plugins.middleware.plugin import HttpRequest
from apps.plugins.views import PluginConfigurationViewMixin
from apps.sections.views.mixins.membership import EnsureLocalUserViewMixin
from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin
from apps.utils.models.query import Q


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
    EnsureInSectionSpaceViewMixin,
    EnsureLocalUserViewMixin,
    PermissionRequiredMixin,
    PluginConfigurationViewMixin[BuddySystemConfiguration],
    BaseDetailView,
):
    def has_permission(self):
        return self.configuration.matching_policy_instance.can_member_match

    def get_queryset(self):
        return self.configuration.matching_policy_instance.limit_requests(
            qs=BuddyRequest.objects.get_queryset(),
            membership=self.request.membership,
        )

    def post(self, request, pk: uuid.UUID):
        BuddyRequest.objects.match_by(
            request=self.get_object(),
            matcher=self.request.user,
        )

        messages.success(request, _("Request successfully matched!"))
        # TODO: target URL?
        return HttpResponseClientRedirect("/")


class ProfilePictureServeView(
    PluginConfigurationViewMixin[BuddySystemConfiguration],
    NamespacedFilesServeView,
):
    def has_permission(self, request: HttpRequest, name: str) -> bool:
        # is the file in requests, for whose is the related section responsible?
        related_requests = request.membership.section.buddy_system_requests.filter(
            Q(issuer__profile__picture=name) | Q(matched_by__profile__picture=name)
        )

        # does have the section enabled picture displaying?
        return (related_requests.exists() and self.configuration and self.configuration.display_issuer_picture) or (
            related_requests.filter(
                Q(matched_by=request.user) | Q(issuer=request.user), state=BuddyRequest.State.MATCHED
            ).exists()
        )
