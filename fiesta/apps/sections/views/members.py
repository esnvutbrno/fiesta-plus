import django_tables2 as tables
from django.contrib.postgres.search import SearchVector
from django.forms import TextInput
from django.utils.translation import gettext_lazy as _
from django_filters import ChoiceFilter, CharFilter, ModelChoiceFilter
from django_tables2 import Column

from apps.fiestatables.columns import ImageColumn, LabeledChoicesColumn
from apps.fiestatables.filters import BaseFilterSet, ProperDateFromToRangeFilter
from apps.fiestatables.views.tables import FiestaTableView
from apps.sections.middleware.user_membership import HttpRequest
from apps.sections.models import SectionMembership
from apps.universities.models import Faculty
from apps.utils.breadcrumbs import with_breadcrumb


def related_faculties(request: HttpRequest):
    return Faculty.objects.filter(university__section=request.membership.section)


class SectionMembershipFilter(BaseFilterSet):
    search = CharFilter(
        method="filter_search",
        label=_("Search"),
        widget=TextInput(attrs={"placeholder": _("Hannah, Diego, Joe...")}),
    )
    user__profile__home_faculty = ModelChoiceFilter(
        queryset=related_faculties, label=_("Faculty")
    )
    state = ChoiceFilter(choices=SectionMembership.State.choices, label=_("State"))

    # created = DateRangeFilter()
    created_when = ProperDateFromToRangeFilter(field_name="created", label=_("Joined"))

    class Meta(BaseFilterSet.Meta):
        pass

    def filter_search(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector("user__last_name", "user__first_name", "state", "role")
        ).filter(search=value)


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

    state = LabeledChoicesColumn(
        SectionMembership.State,
        {
            SectionMembership.State.UNCONFIRMED: "❓",
            SectionMembership.State.ACTIVE: "✅",
            SectionMembership.State.BANNED: "⛔",
        },
    )

    class Meta:
        model = SectionMembership

        fields = ("state", "created")

        sequence = (
            "user__full_name_official",
            "user__profile__picture",
            "user__profile__home_faculty__abbr",
            "...",
        )


@with_breadcrumb(_("Section"))
@with_breadcrumb(_("Members"))
class SectionMembersView(FiestaTableView):
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
