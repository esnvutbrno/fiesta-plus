from __future__ import annotations

import operator
import random

import factory
from factory import SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyAttribute, FuzzyChoice

from apps.accounts.conf import INTERESTS_CHOICES
from apps.accounts.models import User
from apps.buddy_system.models import BuddyRequest
from apps.sections.models import Section


class BuddyRequestWithUserFactory(DjangoModelFactory):
    class Meta:
        model = BuddyRequest

    issuer = SubFactory(
        "apps.utils.factories.accounts.UserSingleMembershipFactory",
    )
    responsible_section = FuzzyChoice(
        Section.objects.all(),
    )
    state = BuddyRequest.State.CREATED

    interests = FuzzyAttribute(
        lambda: tuple(
            map(
                operator.itemgetter(0),
                random.sample(
                    sorted(INTERESTS_CHOICES),
                    random.randint(0, int(0.6 * len(INTERESTS_CHOICES))),
                ),
            )
        ),
    )

    note = factory.Faker("text", max_nb_chars=600)


class BuddyRequestWithKnownUserFactory(BuddyRequestWithUserFactory):
    issuer = FuzzyChoice(
        User.objects.all(),
    )
