from __future__ import annotations

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.utils.models import BaseTimestampedModel


class NotificationKind(models.TextChoices):
    BUDDY_MATCHED_ISSUER = "buddy_matched_issuer", _("Buddy matched — issuer")
    PICKUP_MATCHED_ISSUER = "pickup_matched_issuer", _("Pickup matched — issuer")
    MEMBER_WAITING_DIGEST = "member_waiting_digest", _("New member waiting digest")


class ScheduledNotification(BaseTimestampedModel):
    """
    A notification that must be sent at a future point in time.

    Used for delayed issuer emails (~1 h after matching, giving editors time to correct
    mistakes) and for editor member-waiting digests.
    """

    Kind = NotificationKind

    kind = models.CharField(
        max_length=64,
        choices=NotificationKind.choices,
        verbose_name=_("kind"),
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="scheduled_notifications",
        verbose_name=_("recipient"),
    )
    section = models.ForeignKey(
        "sections.Section",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="scheduled_notifications",
        verbose_name=_("section"),
    )

    # Generic FK to the triggering object (match, membership, …).  SET_NULL so a
    # dangling reference after object deletion doesn't hard-error — the management
    # command handles NULL gracefully.
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("content type"),
    )
    object_id = models.UUIDField(null=True, blank=True, verbose_name=_("object id"))
    content_object = GenericForeignKey("content_type", "object_id")

    send_after = models.DateTimeField(verbose_name=_("send after"))
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name=_("sent at"))
    cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name=_("cancelled at"))

    class Meta:
        verbose_name = _("scheduled notification")
        verbose_name_plural = _("scheduled notifications")
        indexes = [
            models.Index(fields=["send_after", "sent_at", "cancelled_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.get_kind_display()} → {self.recipient} @ {self.send_after:%Y-%m-%d %H:%M}"

    @property
    def is_pending(self) -> bool:
        return self.sent_at is None and self.cancelled_at is None

    def cancel(self) -> None:
        """Mark this notification as cancelled (does NOT save — caller must .save())."""
        self.cancelled_at = timezone.now()
