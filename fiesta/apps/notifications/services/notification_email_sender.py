from __future__ import annotations

import logging

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _

from apps.notifications.models import ScheduledNotification
from apps.notifications.models.scheduled import NotificationKind

logger = logging.getLogger(__name__)

# Maps each NotificationKind to its template basename (without extension).
# Both a .txt subject template and a .txt body template exist per kind.
_TEMPLATE_MAP: dict[str, str] = {
    NotificationKind.BUDDY_MATCHED_ISSUER: "notifications/buddy_system/matched_issuer",
    NotificationKind.PICKUP_MATCHED_ISSUER: "notifications/pickup_system/matched_issuer",
    NotificationKind.MEMBER_WAITING_DIGEST: "notifications/sections/member_waiting_digest",
}


class NotificationEmailSender:
    """
    Renders and sends a single ScheduledNotification via Django's email backend.

    Template conventions
    --------------------
    For each notification kind there must be two templates:
    - ``<basename>_subject.txt``   — rendered, stripped, used as the subject line
    - ``<basename>_body.txt``      — rendered as the plain-text body

    Both templates receive ``notification`` and ``object`` (the content_object)
    in their context.
    """

    def send(self, notification: ScheduledNotification) -> bool:
        """
        Render and dispatch a single scheduled notification.

        Returns True when the mail was dispatched, False when skipped
        (e.g. no email address, template missing, etc.).
        Does NOT update sent_at — the caller is responsible for that.
        """
        template_basename = _TEMPLATE_MAP.get(notification.kind)
        if not template_basename:
            logger.error("Unknown notification kind: %s", notification.kind)
            return False

        recipient_email = self._resolve_recipient_email(notification)
        if not recipient_email:
            logger.warning(
                "Skipping notification %s — recipient has no email address",
                notification.pk,
            )
            return False

        context = {
            "notification": notification,
            "object": notification.content_object,
            "recipient": notification.recipient,
            "section": notification.section,
        }

        subject = render_to_string(f"{template_basename}_subject.txt", context).strip()
        body = render_to_string(f"{template_basename}_body.txt", context)

        from_email = self._resolve_from_email(notification)

        send_mail(
            subject=subject,
            message=body,
            from_email=from_email,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        logger.info(
            "Sent %s notification %s to %s",
            notification.kind,
            notification.pk,
            recipient_email,
        )
        return True

    def _resolve_recipient_email(self, notification: ScheduledNotification) -> str | None:
        """Return the recipient's email address, or None if unavailable."""
        try:
            return notification.recipient.user.email or None
        except Exception:
            return None

    def _resolve_from_email(self, notification: ScheduledNotification) -> str:
        """Return the from-address for the given notification."""
        section = notification.section
        section_name = getattr(section, "name", _("fiesta.plus"))
        return f"{section_name} via fiesta.plus <noreply@fiesta.plus>"


sender = NotificationEmailSender()

__all__ = ["NotificationEmailSender", "sender"]
