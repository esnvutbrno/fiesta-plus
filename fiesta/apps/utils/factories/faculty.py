from __future__ import annotations

import factory
from factory import SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice
from faker_education import SchoolProvider

from apps.universities.models import Faculty

factory.Faker.add_provider(SchoolProvider)

FACULTIES = {
    "Faculty of Classics",
    "Faculty of Commerce",
    "Faculty of Economics",
    "Faculty of Education",
    "Faculty of Engineering",
    "Faculty of Information Technology",
    "Faculty of Humanities",
    "Faculty of Natural Sciences",
    "Faculty of Political Science",
}


class FacultyFactory(DjangoModelFactory):
    class Meta:
        model = Faculty
        django_get_or_create = ("name",)

    name = FuzzyChoice(FACULTIES)
    abbr = factory.LazyAttribute(lambda u: "".join((bit[0] if bit else "") for bit in u.name.split(" ")))

    university = SubFactory(
        "apps.utils.factories.universities.UniversityFactory",
    )
