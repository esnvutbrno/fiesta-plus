import enum

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from apps.utils.models import BaseTimestampedModel


class UserProfile(BaseTimestampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name="profile",
        verbose_name=_("user"),
    )

    nationality = CountryField(blank=True, verbose_name=_("nationality"))

    # TODO: define relation to section, membership, universities
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

    # TODO: define formfield/widget to handle flagging
    preferences = models.PositiveSmallIntegerField(
        default=0, verbose_name=_("user preferences as flags")
    )

    class Meta:
        verbose_name = _("user profile")
        verbose_name_plural = _("user profiles")


__all__ = ["UserProfile"]
