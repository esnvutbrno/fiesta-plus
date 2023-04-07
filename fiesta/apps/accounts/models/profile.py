from __future__ import annotations

import enum
import typing

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import CharField, CheckConstraint, TextChoices
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from django_lifecycle import AFTER_SAVE, LifecycleModelMixin, hook
from phonenumber_field.modelfields import PhoneNumberField

from apps.files.storage import NamespacedFilesStorage
from apps.utils.models import BaseTimestampedModel
from apps.utils.models.query import Q

if typing.TYPE_CHECKING:
    from apps.plugins.middleware.plugin import HttpRequest


def has_permission_for_profile_picture_view(request: "HttpRequest", name: str) -> bool:
    if (membership := request.membership) and membership.is_privileged:
        return True

    if not (profile := request.user.profile_or_none):  # type: UserProfile
        return False

    return profile.picture.name == name


# storage used for profile pictures, serving directly only for privileged and for user itself
user_profile_picture_storage = NamespacedFilesStorage(
    "profile-picture",
    has_permission=has_permission_for_profile_picture_view,
)


class UserProfileState(TextChoices):
    # CREATED = 'created', _('Created')
    INCOMPLETE = "incomplete", _("Uncompleted")
    COMPLETE = "complete", _("Completed")


class UserProfile(LifecycleModelMixin, BaseTimestampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name="profile",
        verbose_name=_("user"),
    )

    # ### FIELDS, which are conditionally REQUIRED ###
    # see AccountsConfiguration

    nationality = CountryField(
        verbose_name=_("nationality"),
        blank=True,
        null=True,
    )

    class Gender(TextChoices):
        MALE = "male", _("male")
        FEMALE = "female", _("female")
        DECLINE_TO_STATE = "decline_to_state", _("decline to state")
        OTHER = "other", _("other")

    gender = CharField(
        verbose_name=_("gender"),
        blank=True,
        null=True,
        choices=Gender.choices,
        max_length=16,
    )

    home_university = models.ForeignKey(
        "universities.University",
        on_delete=models.RESTRICT,
        verbose_name=_("home university"),
        help_text=_("home university for all users"),
        related_name="home_university_user_profiles",
        null=True,
        blank=True,
        db_index=True,
    )
    home_faculty = models.ForeignKey(
        "universities.Faculty",
        on_delete=models.RESTRICT,
        verbose_name=_("home faculty"),
        # TODO: help, not description
        help_text=_("home faculty for members, empty for internationals"),
        related_name="home_faculty_user_profiles",
        null=True,
        blank=True,
        db_index=True,
    )

    guest_faculty = models.ForeignKey(
        "universities.Faculty",
        on_delete=models.RESTRICT,
        verbose_name=_("guest faculty"),
        help_text=_("guest faculty for international students, empty for members"),
        related_name="guest_user_profiles",
        blank=True,
        null=True,
        db_index=True,
    )

    picture = models.ImageField(
        storage=user_profile_picture_storage,
        upload_to=user_profile_picture_storage.upload_to,
        verbose_name=_("profile picture"),
        null=True,
        blank=True,
    )

    # TODO: social network profiles

    phone_number = PhoneNumberField(
        null=True, blank=True, verbose_name=_("phone number")
    )

    @enum.unique
    class Preferences(enum.Flag):
        WEEKLY_UPDATES = enum.auto()
        # TODO: push notifications & emails

    # TODO: define formfield/widget to handle flagging
    preferences = models.PositiveSmallIntegerField(
        default=0, verbose_name=_("user preferences as flags")
    )

    State = UserProfileState

    state = models.CharField(
        verbose_name=_("state"),
        max_length=16,
        choices=State.choices,
        default=State.INCOMPLETE,
    )

    class Meta:
        verbose_name = _("user profile")
        verbose_name_plural = _("user profiles")
        constraints = (
            CheckConstraint(
                # home university XOR home faculty
                check=Q(state=UserProfileState.INCOMPLETE.value)
                | (Q(home_university=None) ^ Q(home_faculty=None)),
                name="home_university_or_faculty",
            ),
        )

    def clean(self):
        super().clean()

        if not (bool(self.home_university) ^ bool(self.home_faculty)):
            raise ValidationError(
                {
                    "home_university": _(
                        # TODO: weird, basically it's exactly one of these
                        "At least one from home university/faculty has to be set."
                    )
                }
            )

    @hook(AFTER_SAVE)
    def on_save(self):
        from apps.accounts.services import UserProfileStateSynchronizer

        UserProfileStateSynchronizer.on_user_profile_update(profile=self)

    def __str__(self):
        return (
            f"{self.user} {self.nationality} "
            f"{self.home_university or (self.home_faculty.university if self.home_faculty else None) or ''} "
        )


__all__ = [
    "UserProfile",
    "user_profile_picture_storage",
]
