from __future__ import annotations

import typing

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import ModificationDateTimeField

if typing.TYPE_CHECKING:
    from apps.accounts.models import UserProfile


class User(AbstractUser):
    class State(models.TextChoices):
        REGISTERED = "registered", _("Registered")
        ACTIVE = "active", _("Active")
        EXPIRED = "expired", _("Expired")
        BANNED = "banned", _("Banned")

    state = models.CharField(
        choices=State.choices,
        default=State.REGISTERED,
        max_length=16,
        verbose_name=_("state"),
        help_text=_("current state of user (different from user profile state)"),
    )

    modified = ModificationDateTimeField(verbose_name=_("modified"))

    @property
    def profile_or_none(self) -> UserProfile | None:
        from apps.accounts.models import UserProfile

        try:
            return self.profile
        except UserProfile.DoesNotExist:
            ...

    @property
    def full_name(self):
        return self.get_full_name()

    @property
    def full_name_official(self):
        return f"{self.last_name} {self.first_name}".strip()

    class Meta(AbstractUser.Meta):
        verbose_name = _("user")
        verbose_name_plural = _("users")

    # a few dynamic related models
    buddy_system_request_matches: models.QuerySet
    profile: UserProfile

    @property
    def primary_email(self):
        return self.emailaddress_set.filter(primary=True).first() or self.email


__all__ = ["User"]
