from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.utils.models import BaseTimestampedModel


class Role(models.TextChoices):
    EVENT_LEADER = "event_leader", _("Event_leader")
    OC = "oc", _("OC")


class Organizer(BaseTimestampedModel):
    state = models.CharField(
        choices=Role.choices,
        default=Role.OC,
        verbose_name=_("state"),
        help_text=_("current state of the event"),
    )

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="event",
        verbose_name=_("user"),
        db_index=True,
    )

    event = models.ForeignKey(
        "events.Event",
        on_delete=models.CASCADE,
        related_name="organizer",
        verbose_name=_("event"),
        db_index=True,
    )

    class Meta:
        verbose_name = _("organizer")
        verbose_name_plural = _("organizers")
        unique_together = (("user", "event"),)

    def __str__(self):
        return self.user + self.event


__all__ = ["Organizer"]
