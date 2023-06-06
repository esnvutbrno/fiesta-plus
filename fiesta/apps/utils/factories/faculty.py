from __future__ import annotations

import factory
from factory import SubFactory
from factory.django import DjangoModelFactory
from faker_education import SchoolProvider

from apps.universities.models import Faculty

factory.Faker.add_provider(SchoolProvider)

class FacultyFactory(DjangoModelFactory):
    class Meta:
        model = Faculty
        django_get_or_create = ("name",)

    name = factory.Faker("school_level")
    abbr = factory.LazyAttribute(lambda u: "".join((bit[0] if bit else "") for bit in u.name.split(" ")))

    university = SubFactory(
        "apps.utils.factories.universities.UniversityFactory",
    )
