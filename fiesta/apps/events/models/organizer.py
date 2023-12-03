from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.utils.models import BaseTimestampedModel


class OrganizerRole(models.TextChoices):
    EVENT_LEADER = "event_leader", _("Event_leader")
    OC = "oc", _("OC")


class Organizer(BaseTimestampedModel):
    role = models.CharField(
        choices=OrganizerRole.choices,
        default=OrganizerRole.OC,
        verbose_name=_("role"),
        help_text=_("current role of the user on event"),
    )

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="organizer",
        verbose_name=_("user"),
        db_index=True,
    )

    event = models.ForeignKey(
        "events.Event",
        on_delete=models.CASCADE,
        related_name="organizers",
        verbose_name=_("event"),
        db_index=True,
    )

    class Meta:
        verbose_name = _("organizer")
        verbose_name_plural = _("organizers")
        unique_together = (("user", "event"),)

    def __str__(self):
        return f"{self.user} - {self.event}"


__all__ = ["Organizer"]
