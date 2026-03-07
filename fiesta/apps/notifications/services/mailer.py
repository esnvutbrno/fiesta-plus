from __future__ import annotations

import logging
import typing
from typing import Any

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

if typing.TYPE_CHECKING:
    from apps.accounts.models import User


def send_notification_email(
    *,
    subject: str,
    recipient_email: str,
    template_prefix: str,
    context: dict[str, Any],
    recipient_user: User | None = None,
) -> None:
    """
    Render HTML + plain-text email templates and send via django-mailer.

    template_prefix: e.g. "notifications/buddy_system/matched_matcher"
    Templates expected: {template_prefix}.html and {template_prefix}.txt
    """
    if recipient_user is not None and hasattr(recipient_user, "profile"):
        try:
            if not recipient_user.profile.email_notifications_enabled:
                logger.info("Skipping email to user pk=%s: global opt-out", recipient_user.pk)
                return
        except ObjectDoesNotExist:
            pass  # No profile — proceed with sending

    html_content = render_to_string(f"{template_prefix}.html", context)
    text_content = render_to_string(f"{template_prefix}.txt", context)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient_email],
    )
    msg.attach_alternative(html_content, "text/html")

    try:
        msg.send()
    except Exception:
        logger.exception(
            "Failed to send notification email (template: %s)",
            template_prefix,
        )
        raise
