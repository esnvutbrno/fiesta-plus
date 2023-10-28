from __future__ import annotations

from _operator import attrgetter
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import DetailView

from apps.buddy_system.models import BuddyRequest
from apps.buddy_system.views.editor import BuddyRequestsTable
from apps.fiestatables.views.tables import FiestaMultiTableMixin
from apps.sections.models import SectionMembership
from apps.sections.views.mixins.membership import EnsurePrivilegedUserViewMixin
from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin
from apps.utils.breadcrumbs import BreadcrumbItem, with_breadcrumb, with_callable_breadcrumb, with_object_breadcrumb


def page_title(view: DetailView | View) -> BreadcrumbItem:
    m: SectionMembership = view.object
    return (
        BreadcrumbItem(
            title=_("Members"),
            url=reverse("sections:section-members"),
        )
        if m.is_local
        else BreadcrumbItem(
            title=_("Internationals"),
            url=reverse("sections:section-internationals"),
        )
    )


@with_breadcrumb(_("Section"))
@with_callable_breadcrumb(getter=page_title)
@with_object_breadcrumb(prefix=None, getter=attrgetter("user.full_name"))
class MembershipDetailView(
    EnsurePrivilegedUserViewMixin,
    EnsureInSectionSpaceViewMixin,
    FiestaMultiTableMixin,
    DetailView,
):
    model = SectionMembership
    object: SectionMembership
    template_name = "accounts/user_detail/user_detail.html"

    extra_context = {}

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(
            {
                "table_titles": (_("🧑‍🤝‍🧑 Buddies") if self.object.is_local else _("🧑‍🤝‍🧑 Buddy requests"),),
            }
        )
        return data

    def get_tables(self):
        if self.object.is_local:
            return [
                BuddyRequestsTable(
                    request=self.request,
                    data=BuddyRequest.objects.filter(match__matcher=self.object.user),
                    exclude=(
                        "matcher_name",
                        "matcher_picture",
                        "match_request",
                    ),
                ),
            ]

        return [
            BuddyRequestsTable(
                request=self.request,
                data=BuddyRequest.objects.filter(issuer=self.object.user),
                exclude=(
                    "issuer_name",
                    "issuer_picture",
                    # "matcher_picture",
                    # "match_request",
                ),
            ),
        ]

    def get_queryset(self):
        return self.request.in_space_of_section.memberships
