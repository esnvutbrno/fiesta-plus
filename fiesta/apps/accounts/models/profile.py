import enum

from django.conf import settings
from django.db import models
from django_countries.fields import CountryField

from apps.utils.models import BaseTimestampedModel


class UserProfile(BaseTimestampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name="profile",
    )

    nationality = CountryField(blank=True)

    # TODO: define relation to section, membership, university
    # home_faculty = models.ForeignKey(
    #     "core.Faculty",
    #     on_delete=models.RESTRICT,
    #     related_name="home_users",
    # )
    #
    # guest_faculty = models.ForeignKey(
    #     "core.Faculty",
    #     on_delete=models.RESTRICT,
    #     related_name="guest_users",
    #     blank=True,
    # )

    # TODO: profile picture
    picture = models.CharField

    # TODO: phone, profiles

    @enum.unique
    class Preferences(enum.Flag):
        WEEKLY_UPDATES = enum.auto()
        # TODO: push & emails

    preferences = models.PositiveSmallIntegerField(default=0)


__all__ = ["UserProfile"]
