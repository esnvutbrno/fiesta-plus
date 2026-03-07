from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.utils.models import BaseTimestampedModel


class SectionNotificationPreferences(BaseTimestampedModel):
    """Per-user, per-section notification opt-in preferences."""

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="notification_preferences",
        verbose_name=_("user"),
    )
    section = models.ForeignKey(
        "sections.Section",
        on_delete=models.CASCADE,
        related_name="notification_preferences",
        verbose_name=_("section"),
    )

    notify_on_match = models.BooleanField(
        default=True,
        verbose_name=_("notify on match"),
        help_text=_("Receive an email when a buddy/pickup request is matched."),
    )
    notify_on_new_member_waiting = models.BooleanField(
        default=True,
        verbose_name=_("notify on new member waiting"),
        help_text=_(
            "Receive an email digest when new members are waiting for confirmation. "
            "Only relevant for editors and admins."
        ),
    )

    class Meta:
        verbose_name = _("section notification preference")
        verbose_name_plural = _("section notification preferences")
        unique_together = [("user", "section")]

    def __str__(self) -> str:
        return f"{self.user} @ {self.section}"
