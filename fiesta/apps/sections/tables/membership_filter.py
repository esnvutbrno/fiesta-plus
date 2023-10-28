from __future__ import annotations

from django.contrib.postgres.search import SearchVector
from django.forms import TextInput
from django.utils.translation import gettext_lazy as _
from django_filters import CharFilter, ChoiceFilter, ModelChoiceFilter

from apps.fiestatables.filters import BaseFilterSet, ProperDateFromToRangeFilter
from apps.plugins.middleware.plugin import HttpRequest
from apps.sections.models import SectionMembership
from apps.universities.models import Faculty


def related_faculties(request: HttpRequest):
    return Faculty.objects.filter(university__section=request.in_space_of_section)


class SectionMembershipFilter(BaseFilterSet):
    search = CharFilter(
        method="filter_search",
        label=_("Search"),
        widget=TextInput(attrs={"placeholder": _("Hannah, Diego, Joe...")}),
    )
    user__profile__faculty = ModelChoiceFilter(queryset=related_faculties, label=_("Faculty"))
    state = ChoiceFilter(choices=SectionMembership.State.choices, label=_("State"))

    # created = DateRangeFilter()
    created_when = ProperDateFromToRangeFilter(field_name="created", label=_("Joined"))

    class Meta(BaseFilterSet.Meta):
        pass

    def filter_search(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector("user__last_name", "user__first_name", "state", "role"),
        ).filter(
            search=value,
        )
