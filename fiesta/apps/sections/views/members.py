from __future__ import annotations

import django_tables2 as tables
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.postgres.search import SearchVector
from django.forms import TextInput
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView
from django_filters import CharFilter, ChoiceFilter, ModelChoiceFilter
from django_tables2 import Column, TemplateColumn

from apps.fiestaforms.views.htmx import HtmxFormMixin
from apps.fiestatables.columns import ImageColumn, NaturalDatetimeColumn
from apps.fiestatables.filters import BaseFilterSet, ProperDateFromToRangeFilter
from apps.fiestatables.views.tables import FiestaTableView
from apps.sections.forms.membership import ChangeMembershipStateForm
from apps.sections.middleware.user_membership import HttpRequest
from apps.sections.models import SectionMembership
from apps.sections.views.mixins.membership import EnsurePrivilegedUserViewMixin
from apps.universities.models import Faculty
from apps.utils.breadcrumbs import with_breadcrumb, with_object_breadcrumb
from apps.utils.views import AjaxViewMixin


def related_faculties(request: HttpRequest):
    return Faculty.objects.filter(university__section=request.in_space_of_section)


class SectionMembershipFilter(BaseFilterSet):
    search = CharFilter(
        method="filter_search",
        label=_("Search"),
        widget=TextInput(attrs={"placeholder": _("Hannah, Diego, Joe...")}),
    )
    user__profile__home_faculty = ModelChoiceFilter(queryset=related_faculties, label=_("Faculty"))
    state = ChoiceFilter(choices=SectionMembership.State.choices, label=_("State"))

    # created = DateRangeFilter()
    created_when = ProperDateFromToRangeFilter(field_name="created", label=_("Joined"))

    class Meta(BaseFilterSet.Meta):
        pass

    def filter_search(self, queryset, name, value):
        return queryset.annotate(search=SearchVector("user__last_name", "user__first_name", "state", "role")).filter(
            search=value
        )


class SectionMembershipTable(tables.Table):
    user__full_name_official = Column(
        verbose_name=_("Member"),
        order_by=("user__last_name", "user__first_name", "user__username"),
        linkify=(
            "sections:membership-detail",
            dict(
                pk=tables.A("pk"),
            ),
        ),
        attrs=dict(a={"hx-disable": True}),  # TODO: do it properly
    )
    user__profile__picture = ImageColumn()
    user__profile__home_faculty__abbr = Column(verbose_name=_("Faculty"))

    created = NaturalDatetimeColumn(verbose_name=_("Joined"))

    approve_membership = TemplateColumn(
        template_name="sections/parts/change_membership_state_btn.html",
        exclude_from_export=True,
        order_by="state",
        verbose_name=_("Membership"),
        extra_context={"SectionMembership": SectionMembership},
    )

    class Meta:
        model = SectionMembership

        fields = ("created",)

        sequence = (
            "user__full_name_official",
            "user__profile__picture",
            "user__profile__home_faculty__abbr",
            "...",
        )

        attrs = dict(tbody={"hx-disable": True})


@with_breadcrumb(_("Section"))
@with_breadcrumb(_("Members"))
class SectionMembersView(EnsurePrivilegedUserViewMixin, FiestaTableView):
    request: HttpRequest
    template_name = "fiestatables/page.html"
    table_class = SectionMembershipTable
    filterset_class = SectionMembershipFilter
    model = SectionMembership

    select_related = (
        "user__profile",
        "user__profile__home_faculty",
        "user__profile__home_faculty__university",
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
        )


@with_breadcrumb(_("Membership State"))
@with_object_breadcrumb()
class ChangeMembershipStateView(
    EnsurePrivilegedUserViewMixin,
    SuccessMessageMixin,
    HtmxFormMixin,
    AjaxViewMixin,
    UpdateView,
):
    template_name = "sections/parts/change_membership_state.html"
    ajax_template_name = "sections/parts/change_membership_state_form.html"
    model = SectionMembership
    form_class = ChangeMembershipStateForm

    success_url = reverse_lazy("sections:section-members")
    success_message = _("Section membership state has been changed.")
