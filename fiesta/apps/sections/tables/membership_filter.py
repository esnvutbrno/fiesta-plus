from __future__ import annotations

from django.contrib.postgres.search import SearchVector
from django.forms import TextInput
from django.utils.translation import gettext_lazy as _
from django_countries.fields import Country
from django_filters import CharFilter, ChoiceFilter, ModelChoiceFilter

from apps.accounts.models import UserProfile
from apps.fiestatables.filters import BaseFilterSet
from apps.plugins.middleware.plugin import HttpRequest
from apps.sections.models import SectionMembership
from apps.universities.models import Faculty
from apps.utils.models.query import Q


def related_faculties(request: HttpRequest):
    return Faculty.objects.filter(university__section=request.in_space_of_section)


def related_nationalities():
    return [
        (n, f"{c.unicode_flag} {c.name}")
        for n in UserProfile.objects.exclude(nationality=None).values_list("nationality", flat=True).distinct()
        if (c := Country(n))
    ]


class SectionMembershipFilter(BaseFilterSet):
    search = CharFilter(
        method="filter_search",
        label=_("Search"),
        widget=TextInput(attrs={"placeholder": _("Hannah, Diego, Joe...")}),
    )
    user__profile__faculty = ModelChoiceFilter(queryset=related_faculties, label=_("Faculty"))
    user__profile__nationality = ChoiceFilter(choices=related_nationalities, label=_("Nationality"))
    state = ChoiceFilter(choices=SectionMembership.State.choices, label=_("State"))
    role = ChoiceFilter(choices=SectionMembership.Role.choices, label=_("Role"))

    # created = DateRangeFilter()
    # TODO: needed?
    # created_when = ProperDateFromToRangeFilter(field_name="created", label=_("Joined"))

    class Meta(BaseFilterSet.Meta):
        pass

    def filter_search(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector("user__last_name", "user__first_name", "state", "role"),
        ).filter(
            # TODO: find out why search vector is not enough to find "Gus Fring" for "Fri"
            Q(search=value)
            | Q(user__last_name__icontains=value)
            | Q(user__first_name__icontains=value),
        )
