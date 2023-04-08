from django.views.generic import TemplateView

from apps.buddy_system.models import BuddySystemConfiguration
from apps.plugins.views import PluginConfigurationViewMixin
from apps.sections.middleware.user_membership import HttpRequest
from apps.sections.models import SectionMembership
from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin


class BuddySystemIndexView(
    EnsureInSectionSpaceViewMixin,
    PluginConfigurationViewMixin[BuddySystemConfiguration],
    TemplateView,
):
    request: HttpRequest

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        data.update(
            {
                "requests": self.request.user.buddy_system_issued_requests.all().filter(
                    responsible_section=self.request.in_space_of_section
                )
            }
        )
        return data

    def get_template_names(self):
        return [
            (
                "buddy_system/index_international.html"
                if self.request.membership.role == SectionMembership.Role.INTERNATIONAL
                else "buddy_system/index_member.html"
            )
        ]
