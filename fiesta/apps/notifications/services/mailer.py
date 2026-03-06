from __future__ import annotations

import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def send_notification_email(
    *,
    subject: str,
    recipient_email: str,
    template_prefix: str,
    context: dict,
) -> None:
    """
    Render HTML + plain-text email templates and send via django-mailer.

    template_prefix: e.g. "notifications/buddy_system/matched_matcher"
    Templates expected: {template_prefix}.html and {template_prefix}.txt
    """
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
            "Failed to send notification email to %s (template: %s)",
            recipient_email,
            template_prefix,
        )
