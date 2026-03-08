from __future__ import annotations

import logging
import typing
from typing import Any

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from apps.notifications.services.unsubscribe import generate_unsubscribe_token

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

    email_context = dict(context)
    unsubscribe_url = ""
    if recipient_user is not None:
        token = generate_unsubscribe_token(recipient_user.pk)
        unsubscribe_url = f"https://{settings.ROOT_DOMAIN}/notifications/unsubscribe/{token}/"

    email_context["unsubscribe_url"] = unsubscribe_url

    html_content = render_to_string(f"{template_prefix}.html", email_context)
    text_content = render_to_string(f"{template_prefix}.txt", email_context)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient_email],
    )
    if unsubscribe_url:
        email.extra_headers["List-Unsubscribe"] = f"<{unsubscribe_url}>"
        email.extra_headers["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"

    email.attach_alternative(html_content, "text/html")

    try:
        email.send()
    except Exception:
        logger.exception(
            "Failed to send notification email (template: %s)",
            template_prefix,
        )
        raise
