from __future__ import annotations

from django.contrib.postgres.search import SearchVector
from django.forms import TextInput
from django.utils.translation import gettext_lazy as _
from django_filters import CharFilter, ChoiceFilter, ModelChoiceFilter
from django_tables2 import Column, tables
from django_tables2.utils import Accessor

from apps.fiestarequests.models.request import BaseRequestProtocol
from apps.fiestatables.columns import AvatarColumn, NaturalDatetimeColumn
from apps.fiestatables.filters import BaseFilterSet, ProperDateFromToRangeFilter
from apps.plugins.middleware.plugin import HttpRequest
from apps.universities.models import Faculty


def related_faculties(request: HttpRequest):
    return Faculty.objects.filter(university__section=request.in_space_of_section)


class BaseRequestsFilter(BaseFilterSet):
    search = CharFilter(
        method="filter_search",
        label=_("Search"),
        widget=TextInput(attrs={"placeholder": _("Hannah, Diego, Joe...")}),
    )
    state = ChoiceFilter(choices=BaseRequestProtocol.State.choices)
    matched_when = ProperDateFromToRangeFilter(
        field_name="match__created",
    )

    matcher_faculty = ModelChoiceFilter(
        queryset=related_faculties,
        label=_("Faculty of matcher"),
        field_name="match__matcher__profile__faculty",
    )

    def filter_search(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                "issuer__last_name",
                "issuer__first_name",
                "match__matcher__last_name",
                "match__matcher__first_name",
                "state",
            )
        ).filter(search=value)

    class Meta(BaseFilterSet.Meta):
        pass


class BaseRequestsTable(tables.Table):
    issuer_name = Column(
        accessor="issuer.full_name_official",
        order_by=("issuer__last_name", "issuer__first_name", "issuer__username"),
        verbose_name=_("Issuer"),
    )


    issuer_picture = AvatarColumn(accessor="issuer.profile.picture", verbose_name="🧑")
    
    issuer_faculty = Column(
        accessor="issuer.profile_or_none.faculty",
        verbose_name=_("Faculty"),
    )
    
    issuer_nationality = Column(
        accessor="issuer.profile_or_none.nationality",
        verbose_name=_("Nationality"),
    )

    matcher_name = Column(
        accessor="match.matcher.full_name_official",
        order_by=(
            "match__matcher__last_name",
            "match__matcher__first_name",
            "match__matcher__username",
        ),
        linkify=("sections:user-detail", {"pk": Accessor("match.matcher.pk")}),
    )
    matcher_email = Column(
        accessor="match.matcher.email",
        visible=False,
    )

    requested = NaturalDatetimeColumn(verbose_name=_("Requested"), accessor="created")
    
    matched = NaturalDatetimeColumn(
        accessor="match.created",
        verbose_name=_("Matched"),
        attrs={"td": {"title": None}},  # TODO: fix attrs accessor
    )

    class Meta:
        # TODO: dynamic by section preferences
        fields = ("state",)
        sequence = (
            "issuer_name",
            "issuer_picture",
            "issuer_faculty",
            "issuer_nationality",
            "state",
            "...",
            "matcher_name",
            "requested",
            "matched",
            "match_request",
        )

        empty_text = _("No requests found")

        attrs = dict(tbody={"hx-boost": False})
