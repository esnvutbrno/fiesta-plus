from __future__ import annotations

from io import BytesIO
from operator import itemgetter

import factory
import requests
from django.core.files.images import ImageFile
from django_countries.data import COUNTRIES
from factory import fuzzy
from factory.django import DjangoModelFactory

from apps.accounts.models import User, UserProfile


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

        django_get_or_create = ("username",)

    username = factory.Faker("user_name")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")

    is_superuser = False
    is_staff = False

    profile = factory.RelatedFactory("apps.utils.factories.accounts.UserProfileFactory", factory_related_name="user")

    state = User.State.ACTIVE


class UserSingleMembershipFactory(UserFactory):
    membership = factory.RelatedFactory(
        "apps.utils.factories.sections.SectionMembershipFactory",
        factory_related_name="user",
    )


class UserProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile
        django_get_or_create = ("user",)

    home_university = factory.SubFactory(
        "apps.utils.factories.universities.UniversityFactory",
    )
    user = factory.SubFactory("apps.utils.factories.accounts.UserFactory", profile=None)
    nationality = fuzzy.FuzzyChoice(COUNTRIES.items(), getter=itemgetter(0))
    gender = fuzzy.FuzzyChoice(UserProfile.Gender.choices, getter=itemgetter(0))

    picture = factory.LazyAttribute(
        lambda u: ImageFile(
            BytesIO(requests.get(f"https://i.pravatar.cc/150?u={u.user_id}").content),
            "image.jpg",
        )
    )

    facebook = factory.Faker("url")
    instagram = factory.Faker("user_name")
    telegram = factory.Faker("url")
    whatsapp = factory.Faker("phone_number")
