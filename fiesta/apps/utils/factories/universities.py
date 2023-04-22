from __future__ import annotations

import factory
from django_countries import countries
from factory import fuzzy
from factory.django import DjangoModelFactory
from faker_education import SchoolProvider

from apps.universities.models import University

factory.Faker.add_provider(SchoolProvider)


class UniversityFactory(DjangoModelFactory):
    class Meta:
        model = University
        django_get_or_create = ("name",)

    name = factory.Faker("school_name")
    abbr = factory.LazyAttribute(lambda u: "".join((bit[0] if bit else "") for bit in u.name.split(" ")))

    country = fuzzy.FuzzyChoice(countries.countries.items(), getter=lambda c: c[0])
