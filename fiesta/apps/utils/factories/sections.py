from __future__ import annotations

from operator import itemgetter

from django.utils.text import slugify
from django_countries.data import COUNTRIES
from factory import LazyAttribute, SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice

from apps.sections.models import Section, SectionMembership


class KnownSectionFactory(DjangoModelFactory):
    class Meta:
        model = Section
        django_get_or_create = ("name",)

    name = FuzzyChoice(
        (
            "ESN VUT Brno",
            "ESN MUNI",
            "ESN VSB TUO",
            "ISC CTU",
            "ESN MENDELU",
            "ESN Zlin",
        )
    )

    space_slug = LazyAttribute(lambda o: slugify(o.name).replace("-", ""))

    country = FuzzyChoice(COUNTRIES.items(), getter=itemgetter(0))


class SectionMembershipWithUserFactory(DjangoModelFactory):
    class Meta:
        model = SectionMembership

    user = SubFactory(
        "apps.utils.factories.accounts.UserFactory",
    )
    section = SubFactory(
        "apps.utils.factories.sections.KnownSectionFactory",
    )
    role = FuzzyChoice((SectionMembership.Role.MEMBER, SectionMembership.Role.INTERNATIONAL))
    state = SectionMembership.State.ACTIVE
