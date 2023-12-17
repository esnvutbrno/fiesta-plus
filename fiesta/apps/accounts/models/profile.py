from __future__ import annotations

import enum
import typing

from django.conf import settings
from django.db import models
from django.db.models import CharField, TextChoices
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from django_lifecycle import AFTER_SAVE, LifecycleModelMixin, hook
from phonenumber_field.modelfields import PhoneNumberField

from apps.accounts.conf import INTERESTS_CHOICES
from apps.files.storage import NamespacedFilesStorage
from apps.utils.models import BaseTimestampedModel
from apps.utils.models.fields import ArrayFieldWithDisplayableChoices

if typing.TYPE_CHECKING:
    from apps.plugins.middleware.plugin import HttpRequest


def has_permission_for_profile_picture_view(request: HttpRequest, name: str) -> bool:
    if not request.user.is_authenticated:
        return False

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
    # see SectionsConfiguration

    birth_date = models.DateField(
        verbose_name=_("birth date"),
        blank=True,
        null=True,
    )

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
        choices=Gender.choices,
        max_length=16,
    )

    university = models.ForeignKey(
        "universities.University",
        on_delete=models.RESTRICT,
        verbose_name=_("university"),
        related_name="university_user_profiles",
        null=True,
        blank=True,
        db_index=True,
    )
    faculty = models.ForeignKey(
        "universities.Faculty",
        on_delete=models.RESTRICT,
        verbose_name=_("faculty"),
        related_name="faculty_user_profiles",
        null=True,
        blank=True,
        db_index=True,
    )

    picture = models.ImageField(
        storage=user_profile_picture_storage,
        upload_to=user_profile_picture_storage.upload_to,
        verbose_name=_("profile picture"),
        null=True,
        blank=True,
    )

    interests = ArrayFieldWithDisplayableChoices(
        base_field=CharField(
            choices=INTERESTS_CHOICES,
            max_length=24,
            # inner field could be empty (default to remove empty option in .choices)
            default=None,
        ),
        verbose_name=_("interests"),
        default=list,  # as callable to not share instance,
        blank=True,
    )

    facebook = models.CharField(
        verbose_name=_("facebook"),
        blank=True,
        help_text=_("Username or profile link: john.doe or https://www.facebook.com/john.doe"),
    )
    instagram = models.CharField(
        verbose_name=_("instagram"),
        blank=True,
        help_text=_("Username or profile link: john.doe or https://www.instagram.com/john.doe"),
    )
    telegram = models.CharField(
        verbose_name=_("telegram"),
        blank=True,
        help_text=_("Username, phone, or profile: john.doe, +420777888999 or https://t.me/john.doe"),
    )
    whatsapp = models.CharField(
        verbose_name=_("whatsapp"),
        blank=True,
        help_text=_("Phone: +420777888999"),
    )

    phone_number = PhoneNumberField(null=True, blank=True, verbose_name=_("phone number"))

    @enum.unique
    class Preferences(enum.Flag):
        WEEKLY_UPDATES = enum.auto()
        # TODO: push notifications & emails

    # TODO: define formfield/widget to handle flagging
    preferences = models.PositiveSmallIntegerField(default=0, verbose_name=_("user preferences as flags"))

    State = UserProfileState

    state = models.CharField(
        verbose_name=_("state"),
        max_length=16,
        choices=State.choices,
        default=State.INCOMPLETE,
    )

    enforce_revalidation = models.BooleanField(
        verbose_name=_("enforce revalidation of profile"),
        default=False,
    )

    avatar_slug = models.CharField(
        verbose_name=_("avatar slug"),
        max_length=64,
        blank=True,
        default="",
    )

    class Meta:
        verbose_name = _("user profile")
        verbose_name_plural = _("user profiles")

    @hook(AFTER_SAVE)
    def on_save(self):
        from apps.accounts.services.user_profile_state_synchronizer import synchronizer

        # self.user should be saved before the UserProfile form
        synchronizer.revalidate_user_profile(profile=self)

    def __str__(self):
        return (
            f"{self.user} {self.nationality} "
            f"{self.university or (self.faculty.university if self.faculty else None) or ''} "
        )

    def is_esn_card_holder(self):
        return False


__all__ = [
    "UserProfile",
    "user_profile_picture_storage",
]
