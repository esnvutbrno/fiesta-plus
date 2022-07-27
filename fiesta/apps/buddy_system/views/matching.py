from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView

from apps.buddy_system.models import BuddyRequest, BuddySystemConfiguration
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
        return self.configration.matching_policy_instance.can_member_match

    def get_queryset(self):
        return self.configration.matching_policy_instance.limit_requests(
            qs=BuddyRequest.objects.get_queryset(),
            membership=self.request.membership,
        )
