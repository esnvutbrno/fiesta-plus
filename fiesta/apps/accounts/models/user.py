from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField


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

    created = CreationDateTimeField(verbose_name=_("created"))
    modified = ModificationDateTimeField(verbose_name=_("modified"))

    class Meta(AbstractUser.Meta):
        verbose_name = _("user")
        verbose_name_plural = _("users")


__all__ = ["User"]
