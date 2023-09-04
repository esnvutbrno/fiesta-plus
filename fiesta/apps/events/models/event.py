from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.files.storage import NamespacedFilesStorage
from apps.plugins.middleware.plugin import HttpRequest
from apps.utils.models import BaseTimestampedModel
from django.conf import settings


class State(models.TextChoices):
    CREATED = "created", _("Created")
    APPROVED = "approved", _("Approved")
    DECLINED = "declined", _("Declined")
    BANNED = "banned", _("Banned")


def has_permission_for_cover_photo_view(request: HttpRequest, name: str) -> bool:  # TODO
    if request.user.is_authenticated:
        return True

    return False


class Event(BaseTimestampedModel):
    # storage used for cover photos
    event_cover_photo_storage = NamespacedFilesStorage(
        "event-cover-photo",
        has_permission=has_permission_for_cover_photo_view,
    )

    title = models.CharField(
        max_length=64,
        unique=True,
        verbose_name=_("title"),
        help_text=_("full name of the event"),
    )

    subtitle = models.TextField(
        verbose_name=_("subtitle"),
        help_text=_("short description of the event"),
    )

    description = models.TextField(
        verbose_name=_("description"),
        help_text=_("full description of the event"),
    )

    capacity = models.SmallIntegerField(
        verbose_name=_("capacity"),
        help_text=_("capacity of the event"),
    )

    state = models.CharField(
        choices=State.choices,
        default=State.CREATED,
        max_length=16,
        verbose_name=_("state"),
        help_text=_("current state of the event"),
    )

    start = models.DateTimeField(
        verbose_name=_("start"),
        help_text=_("when the event starts"),
    )

    end = models.DateTimeField(
        verbose_name=_("end"),
        help_text=_("when the event ends"),
        null=True,
        blank=True,
    )

    # TODO jak s místem? samostatná tabulka? a co coordinates?

    place = models.CharField(
        max_length=64,
        unique=True,
        verbose_name=_("place"),
        help_text=_("where is the event taking place"),
    )

    meeting_place = models.CharField(
        max_length=64,
        verbose_name=_("meeting_place"),
        help_text=_("where are student meeting before the event"),
        null=True,
        blank=True,
    )

    meeting_coordinates = models.CharField(
        max_length=64,
        verbose_name=_("meeting_coordinated"),
        help_text=_("where are student meeting before the event"),
        null=True,
        blank=True,
    )

    cover = models.ImageField(
        storage=event_cover_photo_storage,
        upload_to=event_cover_photo_storage.upload_to,
        verbose_name=_("cover photo"),
        null=True,
        blank=True,
    )

    organizer = models.ManyToOneRel(  # TODO authorisation
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="event",
    )

    confirmer = models.ManyToOneRel(  # TODO authorisation
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="event",
    )

    section = models.ManyToManyRel(  # TODO authorisation // should we consider BU
        related_name="event",
    )

    def __str__(self):
        return self.title


__all__ = ["Event"]
