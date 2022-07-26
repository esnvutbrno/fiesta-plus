from django.views.generic import ListView

from apps.buddy_system.models import BuddyRequest
from apps.sections.middleware.section_space import HttpRequest
from apps.sections.views.space_mixin import EnsureInSectionSpaceViewMixin


class MatchingRequestsView(EnsureInSectionSpaceViewMixin, ListView):
    request: HttpRequest
    template_name = "buddy_system/matching_requests.html"

    model = BuddyRequest

    def get_queryset(self):
        return BuddyRequest.objects.filter(
            responsible_section=self.request.in_space_of_section,
            state=BuddyRequest.State.CREATED,
            matched_by=None,
        ).select_related("issuer")

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(object_list=object_list, **kwargs)

        data.update({"conf": self.request.plugin.configuration})

        return data
