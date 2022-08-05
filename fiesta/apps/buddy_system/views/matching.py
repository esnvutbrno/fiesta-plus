from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView

from apps.buddy_system.models import BuddyRequest, BuddySystemConfiguration
from apps.files.views import NamespacedFilesServeView
from apps.plugins.middleware.plugin import HttpRequest
from apps.plugins.views import PluginConfigurationViewMixin
from apps.sections.views.space_mixin import EnsureInSectionSpaceViewMixin


class MatchingRequestsView(
    EnsureInSectionSpaceViewMixin,
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


class ProfilePictureServeView(
    PluginConfigurationViewMixin[BuddySystemConfiguration], NamespacedFilesServeView
):
    def has_permission(self, request: HttpRequest, name: str) -> bool:
        # is the file in requests, for whose is the related section responsible?
        in_my_section = request.membership.section.buddy_system_requests.filter(
            issuer__profile__picture=name
        ).exists()

        # does have the section enabled picture displaying?
        display = self.configuration and self.configuration.display_issuer_picture

        return in_my_section and display
