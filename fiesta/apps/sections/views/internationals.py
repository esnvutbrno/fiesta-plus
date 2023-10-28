from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from apps.fiestatables.views.tables import FiestaTableView
from apps.plugins.middleware.plugin import HttpRequest
from apps.sections.models import SectionMembership
from apps.sections.tables.internationals import SectionInternationalsTable
from apps.sections.tables.membership_filter import SectionMembershipFilter
from apps.sections.views.mixins.membership import EnsurePrivilegedUserViewMixin
from apps.utils.breadcrumbs import with_breadcrumb


@with_breadcrumb(_("Section"))
@with_breadcrumb(_("Internationals"))
class SectionInternationalsView(EnsurePrivilegedUserViewMixin, FiestaTableView):
    request: HttpRequest
    template_name = "fiestatables/page.html"
    table_class = SectionInternationalsTable
    filterset_class = SectionMembershipFilter
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
        )
