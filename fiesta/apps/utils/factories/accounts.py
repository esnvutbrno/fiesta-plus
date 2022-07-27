from operator import itemgetter

import factory
from django.core.files.base import ContentFile
from django_countries.data import COUNTRIES
from factory import fuzzy
from factory.django import DjangoModelFactory

from apps.accounts.models import User, UserProfile


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("user_name")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")

    is_superuser = False
    is_staff = False

    profile = factory.RelatedFactory(
        "apps.utils.factories.accounts.ProfileFactory", factory_related_name="user"
    )

    state = User.State.ACTIVE


class UserSingleMembershipFactory(UserFactory):
    membership = factory.RelatedFactory(
        "apps.utils.factories.sections.SectionMembershipFactory",
        factory_related_name="user",
    )


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile

    home_university = factory.SubFactory(
        "apps.utils.factories.universities.UniversityFactory",
    )
    user = factory.SubFactory("apps.utils.factories.accounts.UserFactory", profile=None)
    nationality = fuzzy.FuzzyChoice(COUNTRIES.items(), getter=itemgetter(0))
    gender = fuzzy.FuzzyChoice(UserProfile.Gender.choices, getter=itemgetter(0))

    picture = factory.LazyAttribute(
        lambda _: ContentFile(
            factory.django.ImageField()._make_data({"width": 200, "height": 200}),
            "profile.jpg",
        )
    )
