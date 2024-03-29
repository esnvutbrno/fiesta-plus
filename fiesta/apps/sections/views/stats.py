from __future__ import annotations

from django.db import models
from django.db.models import Count, OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_tables2 import Column, Table

from apps.buddy_system.models import BuddyRequest
from apps.fiestatables.filters import BaseFilterSet, ProperDateFromToRangeFilter
from apps.fiestatables.views.tables import FiestaTableView
from apps.sections.views.mixins.membership import EnsurePrivilegedUserViewMixin
from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin
from apps.universities.models import Faculty
from apps.utils.breadcrumbs import with_breadcrumb, with_plugin_home_breadcrumb


class BuddyStatsFilterset(BaseFilterSet):
    matched_at = ProperDateFromToRangeFilter(
        label=_("Matched"),
        method="dummy",
    )

    def dummy(self, qs, *args, **kwargs):
        return qs

    @property
    def qs(self):
        qs = super().qs

        request_counting_qs = BuddyRequest.objects.filter(
            match__matcher_faculty=OuterRef("pk"),
        )

        # TODO: weird, filtering via self.filters keeps lookup_expr as exact
        inner_qs_field = "matched_at"
        if self.form.is_bound and (value := self.form.cleaned_data.get(inner_qs_field)):
            request_counting_qs = ProperDateFromToRangeFilter(field_name=inner_qs_field).filter(
                qs=request_counting_qs,
                value=value,
            )

        return qs.annotate(
            matched_buddy_requests=Coalesce(
                Subquery(
                    request_counting_qs.values("match__matcher_faculty").annotate(count=Count("pk")).values("count"),
                    output_field=models.IntegerField(),
                ),
                0,
            )
        )


class BuddyStatsTable(Table):
    university = Column(
        verbose_name=_("University"), accessor="university.name", attrs=dict(td=dict(title=lambda record: record.name))
    )
    faculty = Column(verbose_name=_("Faculty"), accessor="abbr", attrs=dict(td=dict(title=lambda record: record.name)))
    matched_buddy_requests = Column(
        verbose_name=_("Matched requests"),
        linkify=lambda record: reverse("buddy_system:requests") + f"?matcher_faculty={record.pk}",
    )

    class Meta:
        model = Faculty

        fields = (
            "university",
            "faculty",
            "matched_buddy_requests",
        )


@with_plugin_home_breadcrumb
@with_breadcrumb(_("Statistics"))
class SectionStatsView(EnsurePrivilegedUserViewMixin, EnsureInSectionSpaceViewMixin, FiestaTableView):
    model = Faculty
    table_class = BuddyStatsTable
    filterset_class = BuddyStatsFilterset

    def get_queryset(self, *args, **kwargs):
        return Faculty.objects.filter(
            university__section=self.request.in_space_of_section,
        )
