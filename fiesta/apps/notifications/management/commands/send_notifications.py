from __future__ import annotations

import logging

import djclick as click
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Process and render notifications but do not send or mark as sent.",
)
def command(dry_run: bool):
    """
    Process all pending ScheduledNotifications whose send_after time has passed.

    Intended to be run periodically (e.g., every 5 minutes via cron or Kubernetes CronJob).
    Each notification is processed inside its own atomic transaction so a single
    rendering failure does not block other notifications.
    """
    from apps.notifications.models import ScheduledNotification
    from apps.notifications.services import sender

    now = timezone.now()

    pending = ScheduledNotification.objects.filter(
        send_after__lte=now,
        sent_at__isnull=True,
        cancelled_at__isnull=True,
    ).select_related("recipient__user", "section", "content_type")

    total = pending.count()
    if total == 0:
        click.echo("No pending notifications to send.")
        return

    click.echo(f"Processing {total} pending notification(s) (dry_run={dry_run})...")

    sent_count = 0
    skipped_count = 0
    error_count = 0

    for notification in pending:
        try:
            with transaction.atomic():
                dispatched = sender.send(notification)
                if dispatched and not dry_run:
                    notification.sent_at = timezone.now()
                    notification.save(update_fields=["sent_at"])
                    sent_count += 1
                elif dispatched and dry_run:
                    sent_count += 1
                else:
                    skipped_count += 1
        except Exception as exc:
            logger.exception("Failed to send notification %s: %s", notification.pk, exc)
            error_count += 1

    click.echo(f"Done. sent={sent_count}, skipped={skipped_count}, errors={error_count}.")
