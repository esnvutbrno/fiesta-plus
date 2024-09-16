from __future__ import annotations

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.functional import lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView

from apps.buddy_system.forms import BuddyRequestMatchForm
from apps.buddy_system.models import BuddyRequest, BuddyRequestMatch, BuddySystemConfiguration
from apps.fiestarequests.matching_policy import BaseMatchingPolicy
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

    _policy = None

    def has_permission(self):
        self._policy: BaseMatchingPolicy = self.configuration.matching_policy_instance
        return self._policy.matching_done_by_members and self._policy.can_member_match(
            membership=self.request.membership
        )

    def get_permission_denied_message(self):
        # can be called even in the context of unauthorized user (so no policy available)
        if self._policy and not self._policy.can_member_match(membership=self.request.membership):
            return _("You have reached the limit of request matches in time window.")
        return super().get_permission_denied_message()

    def get_queryset(self):
        return self.configuration.matching_policy_instance.limit_requests(
            qs=BuddyRequest.objects.get_queryset().select_related(
                # select all potentially necessary fields in the template afterward
                "issuer__profile__user",
                "issuer__profile__university",
                "issuer__profile__faculty",
            ),
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

    _policy = None

    def has_permission(self):
        self._policy: BaseMatchingPolicy = self.configuration.matching_policy_instance
        return self._policy.matching_done_by_members and self._policy.can_member_match(
            membership=self.request.membership
        )

    def get_queryset(self):
        return self.configuration.matching_policy_instance.limit_requests(
            qs=BuddyRequest.objects.get_queryset(),
            membership=self.request.membership,
        )

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["note"].help_text = lazy(
            lambda: render_to_string(
                "buddy_system/parts/buddy_request_match_note_help.html",
                context={"request": self.get_object()},
            ),
            str,
        )
        return form


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
