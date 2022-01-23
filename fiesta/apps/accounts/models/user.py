from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField


class User(AbstractUser):
    class State(models.TextChoices):
        REGISTERED = "registered", _("Registered")
        ACTIVE = "active", _("Active")
        BANNED = "banned", _("Banned")

    state = models.CharField(
        choices=State.choices, default=State.REGISTERED, max_length=16
    )

    created = CreationDateTimeField(_("created"))
    modified = ModificationDateTimeField(_("modified"))


__all__ = ["User"]
