import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from django_filters import ChoiceFilter, DateRangeFilter
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin, Column, LazyPaginator

from apps.fiestatables.columns import ImageColumn
from apps.fiestatables.filters import BaseFilterSet, ProperDateFromToRangeFilter
from apps.fiestatables.views.htmx import HtmxTableMixin
from apps.sections.middleware.user_membership import HttpRequest
from apps.sections.models import SectionMembership
from apps.utils.breadcrumbs import with_breadcrumb


class SectionMembershipFilter(BaseFilterSet):
    state = ChoiceFilter(choices=SectionMembership.State.choices)
    role = ChoiceFilter(choices=SectionMembership.Role.choices)
    created = DateRangeFilter()
    created_when = ProperDateFromToRangeFilter(field_name="created")

    class Meta(BaseFilterSet.Meta):
        pass


class MembershipTable(tables.Table):
    user__get_full_name = Column(
        order_by=("user__last_name", "user__first_name", "user__username")
    )

    user__profile__picture = ImageColumn()

    class Meta:
        model = SectionMembership

        fields = ("role", "state", "created")
        sequence = ("user__get_full_name", "user__profile__picture", "...")


@with_breadcrumb(_("Section Members"))
class SectionMembersView(HtmxTableMixin, SingleTableMixin, FilterView):
    request: HttpRequest
    template_name = "fiestatables/page.html"
    table_class = MembershipTable
    filterset_class = SectionMembershipFilter
    paginate_by = 20
    paginator_class = LazyPaginator

    def get_queryset(self):
        return SectionMembership.objects.filter(
            section=self.request.membership.section,
        ).select_related("user__profile")
