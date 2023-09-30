from __future__ import annotations

import uuid

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.utils.translation import gettext as _
from django.views.generic import ListView
from django.views.generic.detail import BaseDetailView
from django_htmx.http import HttpResponseClientRedirect

from apps.buddy_system.models import BuddyRequest, BuddyRequestMatch, BuddySystemConfiguration
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

    @transaction.atomic
    def post(self, request, pk: uuid.UUID):
        br: BuddyRequest = self.get_object()

        match = BuddyRequestMatch(
            request=br,
            matcher=self.request.user,
            note=self.request.POST.get("note"),
        )

        # TODO: check matcher relation to responsible section
        # TODO: reset any previous match for this BR
        match.save()

        br.match = match
        br.state = BuddyRequest.State.MATCHED
        br.save(update_fields=["state"])

        messages.success(request, _("Request successfully matched!"))
        # TODO: target URL?
        return HttpResponseClientRedirect("/")


class IssuerPictureServeView(
    PluginConfigurationViewMixin[BuddySystemConfiguration],
    NamespacedFilesServeView,
):
    def has_permission(self, request: HttpRequest, name: str) -> bool:
        # is the file in requests, for whose is the related section responsible?
        related_requests = request.membership.section.buddy_system_requests.filter(
            issuer__profile__picture=name,
        )

        # does have the section enabled picture displaying?
        return (related_requests.exists() and self.configuration and self.configuration.display_issuer_picture) or (
            related_requests.filter(
                state=BuddyRequest.State.MATCHED,
            )
            .filter(
                Q(match__matcher=request.user) | Q(issuer=request.user),
            )
            .exists()
        )


class MatcherPictureServeView(
    PluginConfigurationViewMixin[BuddySystemConfiguration],
    NamespacedFilesServeView,
):
    def has_permission(self, request: HttpRequest, name: str) -> bool:
        # is the file in requests, for whose is the related section responsible?
        related_requests = request.membership.section.buddy_system_requests.filter(
            match__matcher__profile__picture=name,
        )

        # does have the section enabled picture displaying?
        return (
            related_requests.filter(
                state=BuddyRequest.State.MATCHED,
            )
            .filter(
                Q(match__matcher=request.user) | Q(issuer=request.user),
            )
            .exists()
        )
