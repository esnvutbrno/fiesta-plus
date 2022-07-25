from django.utils.translation import gettext_lazy as _
from django_filters import ChoiceFilter
from django_filters.views import FilterView
from django_tables2 import tables, Column, SingleTableMixin, LazyPaginator

from apps.buddy_system.models import BuddyRequest
from apps.fiestatables.columns import ImageColumn
from apps.fiestatables.filters import BaseFilterSet, ProperDateFromToRangeFilter
from apps.fiestatables.views.htmx import HtmxTableMixin
from apps.sections.middleware.section_space import HttpRequest
from apps.utils.breadcrumbs import with_breadcrumb


class RequestFilter(BaseFilterSet):
    state = ChoiceFilter(choices=BuddyRequest.State.choices)
    created_when = ProperDateFromToRangeFilter(field_name="created")

    class Meta(BaseFilterSet.Meta):
        pass


class RequestTable(tables.Table):
    issuer__get_full_name = Column(
        order_by=("issuer__last_name", "issuer__first_name", "issuer__username")
    )

    issuer__profile__picture = ImageColumn()

    class Meta:
        model = BuddyRequest
        # TODO: dynamic by section preferences
        fields = ("issuer", "state", "created")
        sequence = ("issuer__get_full_name", "issuer__profile__picture", "...")


@with_breadcrumb(_("Requests"))
class RequestsEditorView(HtmxTableMixin, SingleTableMixin, FilterView):
    request: HttpRequest
    template_name = "fiestatables/page.html"
    table_class = RequestTable
    filterset_class = RequestFilter
    paginate_by = 20
    paginator_class = LazyPaginator

    def get_queryset(self):
        return BuddyRequest.objects.filter(
            responsible_section=self.request.in_space_of_section
        ).select_related("issuer__profile")
