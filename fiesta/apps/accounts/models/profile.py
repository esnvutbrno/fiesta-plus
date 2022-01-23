import enum

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import CheckConstraint
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from apps.utils.models import BaseTimestampedModel
from apps.utils.models.query import Q


class UserProfile(BaseTimestampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name="profile",
        verbose_name=_("user"),
    )

    nationality = CountryField(blank=True, verbose_name=_("nationality"))

    # TODO: define relation to section, membership
    home_university = models.ForeignKey(
        "universities.Faculty",
        on_delete=models.RESTRICT,
        verbose_name=_("home university"),
        help_text=_("home university for all users"),
        related_name="home_university_user_profiles",
        null=True,
        blank=True,
    )
    home_faculty = models.ForeignKey(
        "universities.Faculty",
        on_delete=models.RESTRICT,
        verbose_name=_("home faculty"),
        help_text=_("home faculty for members, empty for internationals"),
        related_name="home_faculty_user_profiles",
        null=True,
        blank=True,
    )

    guest_faculty = models.ForeignKey(
        "universities.Faculty",
        on_delete=models.RESTRICT,
        verbose_name=_("guest faculty"),
        help_text=_("guest faculty for international students, empty for members"),
        related_name="guest_user_profiles",
        blank=True,
        null=True,
    )

    # TODO: profile picture
    picture = models.CharField

    # TODO: phone, profiles

    @enum.unique
    class Preferences(enum.Flag):
        WEEKLY_UPDATES = enum.auto()
        # TODO: push notifications & emails

    # TODO: define formfield/widget to handle flagging
    preferences = models.PositiveSmallIntegerField(
        default=0, verbose_name=_("user preferences as flags")
    )

    class Meta:
        verbose_name = _("user profile")
        verbose_name_plural = _("user profiles")
        constraints = (
            CheckConstraint(
                # home university XOR home faculty
                check=Q(home_university=None) ^ Q(home_faculty=None),
                name="home_university_or_faculty",
            ),
        )

    def clean(self):
        super().clean()

        if not (bool(self.home_university) ^ bool(self.home_faculty)):
            raise ValidationError(
                {
                    "home_university": _(
                        "At least one from home university/faculty has to be set."
                    )
                }
            )

    def __str__(self):
        return (
            f"{self.user} {self.nationality} "
            f"{self.home_university or self.home_faculty.university} "
        )


__all__ = ["UserProfile"]
