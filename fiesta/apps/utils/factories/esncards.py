from __future__ import annotations

from operator import itemgetter

import factory
import requests
from django.core.files.images import ImageFile
from django_countries.data import COUNTRIES
from factory import fuzzy
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice
from six import BytesIO

from apps.esncards.models import ESNcardApplication


class ESNCardApplicationFactory(DjangoModelFactory):
    class Meta:
        model = ESNcardApplication

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    birth_date = factory.Faker("date")
    nationality = fuzzy.FuzzyChoice(COUNTRIES.items(), getter=itemgetter(0))
    state = FuzzyChoice(ESNcardApplication.State.values)

    holder_photo = factory.LazyAttribute(
        lambda f: ImageFile(
            BytesIO(requests.get(f"https://i.pravatar.cc/740?u={f.user.username}").content),
            name="image.jpg",
        )
    )

    user = factory.SubFactory(
        "apps.utils.factories.accounts.UserFactory",
    )
    university = factory.SubFactory(
        "apps.utils.factories.universities.UniversityFactory",
    )
    section = factory.SubFactory(
        "apps.utils.factories.sections.KnownSectionFactory",
    )
