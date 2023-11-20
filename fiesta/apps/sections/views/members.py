from __future__ import annotations

from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView

from apps.fiestaforms.views.htmx import HtmxFormViewMixin
from apps.fiestatables.views.tables import FiestaTableView
from apps.sections.forms.membership import ChangeMembershipStateForm
from apps.sections.middleware.user_membership import HttpRequest
from apps.sections.models import SectionMembership
from apps.sections.tables.members import SectionMembershipTable
from apps.sections.tables.membership_filter import SectionMembershipFilter
from apps.sections.views.mixins.membership import EnsurePrivilegedUserViewMixin
from apps.utils.breadcrumbs import with_breadcrumb, with_object_breadcrumb, with_plugin_home_breadcrumb
from apps.utils.views import AjaxViewMixin


@with_plugin_home_breadcrumb
@with_breadcrumb(_("Members"))
class SectionMembersView(EnsurePrivilegedUserViewMixin, FiestaTableView):
    request: HttpRequest
    template_name = "fiestatables/page.html"
    table_class = SectionMembershipTable
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
                role__in=(
                    SectionMembership.Role.MEMBER,
                    SectionMembership.Role.EDITOR,
                    SectionMembership.Role.ADMIN,
                ),
            )
            .order_by("-created")
        )


@with_plugin_home_breadcrumb
@with_breadcrumb(_("Membership State"))
@with_object_breadcrumb()
class ChangeMembershipStateFormView(
    EnsurePrivilegedUserViewMixin,
    SuccessMessageMixin,
    HtmxFormViewMixin,
    AjaxViewMixin,
    UpdateView,
):
    template_name = "sections/parts/change_membership_state.html"
    ajax_template_name = "sections/parts/change_membership_state_form.html"
    model = SectionMembership
    form_class = ChangeMembershipStateForm

    success_url = reverse_lazy("sections:section-members")
    success_message = _("Section membership state has been changed.")
