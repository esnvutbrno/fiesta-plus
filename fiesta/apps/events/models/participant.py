from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.utils.models import BaseModel
from django.conf import settings


class State(models.TextChoices):  # TODO do we need a state if we have an expiration date
    WAITING = "waiting", _("Waiting")
    CONFIRMED = "confirmed", _("Confirmed")
    DELETED = "deleted", _("Deleted")


class Participant(BaseModel):

    created = models.DateTimeField(
        verbose_name=_("created"),
        help_text=_("when the user placed the ordered (does not have to be paid)"),
    )

    user = models.ManyToOneRel(  # TODO authorisation
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="user",
    )

    event = models.ManyToOneRel(  # TODO authorisation
        on_delete=models.SET_NULL,
        related_name="event",
    )

    price = models.ManyToOneRel(  # TODO authorisation
        on_delete=models.SET_NULL,
        related_name="price",
    )

    def __str__(self):
        return self.title


__all__ = ["Participant"]
