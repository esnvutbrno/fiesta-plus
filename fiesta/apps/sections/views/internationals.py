from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from apps.fiestatables.filters import exclude_filters
from apps.fiestatables.views.tables import FiestaTableView
from apps.plugins.middleware.plugin import HttpRequest
from apps.plugins.views import PluginConfigurationViewMixin
from apps.sections.models import SectionMembership, SectionsConfiguration
from apps.sections.tables.internationals import SectionInternationalsTable
from apps.sections.tables.membership_filter import SectionMembershipFilter
from apps.sections.views.mixins.membership import EnsurePrivilegedUserViewMixin
from apps.utils.breadcrumbs import with_breadcrumb, with_plugin_home_breadcrumb


@with_plugin_home_breadcrumb
@with_breadcrumb(_("Internationals"))
class SectionInternationalsView(
    EnsurePrivilegedUserViewMixin,
    PluginConfigurationViewMixin,
    FiestaTableView,
):
    request: HttpRequest
    configuration: SectionsConfiguration
    template_name = "fiestatables/page.html"
    table_class = SectionInternationalsTable
    filterset_class = exclude_filters(SectionMembershipFilter, ("role",))
    model = SectionMembership

    select_related = (
        "user__profile",
        "user__profile__faculty",
        "user__profile__faculty__university",
    )

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                section=self.request.membership.section,
                role=SectionMembership.Role.INTERNATIONAL,
            )
            .order_by("-created")
        )

    def get_table_kwargs(self):
        show_state_btn = (
            not self.configuration.auto_approved_membership_for_international
            or self.get_queryset()
            .filter(state__in=(SectionMembership.State.UNCONFIRMED, SectionMembership.State.BANNED))
            .exists()
        )
        return {
            "exclude": () if show_state_btn else ("state_button",),
        }
