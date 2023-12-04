from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User
from apps.events.models.organizer import OrganizerRole
from apps.events.models.participant import ParticipantState
from apps.files.storage import NamespacedFilesStorage
from apps.plugins.middleware.plugin import HttpRequest
from apps.utils.models import BaseTimestampedModel


# TODO Maybe pre-registration, registration and paused registration for different field.

def has_permission_for_cover_photo_view(request: HttpRequest, name: str) -> bool:  # TODO
    if request.user.is_authenticated:
        return True

    return False


class Event(BaseTimestampedModel):
    # storage used for cover photos
    event_portrait_cover_photo_storage = NamespacedFilesStorage(
        "event-portrait-cover-photo",
        has_permission=has_permission_for_cover_photo_view,
    )

    event_landscape_cover_photo_storage = NamespacedFilesStorage(
        "event-landscape-cover-photo",
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
        blank=True,
        default="",
    )

    description = models.TextField(
        verbose_name=_("description"),
        help_text=_("full description of the event"),
        default="",
    )

    capacity = models.SmallIntegerField(
        verbose_name=_("capacity"),
        help_text=_("capacity of the event"),
    )
    
    class State(models.TextChoices):
        DRAFT = "draft", _("Draft")
        PUBLISHED = "published", _("Published")
        HIDDEN = "hidden", _("Hidden")  # Visible only after invite


    state = models.CharField(
        choices=State.choices,
        default=State.DRAFT,
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

    landscape_cover = models.ImageField(
        storage=event_landscape_cover_photo_storage,
        upload_to=event_landscape_cover_photo_storage.upload_to,
        verbose_name=_("landscape cover photo"),
        null=True,
        blank=True,
    )

    portrait_cover = models.ImageField(
        storage=event_portrait_cover_photo_storage,
        upload_to=event_portrait_cover_photo_storage.upload_to,
        verbose_name=_("portrait cover photo"),
        null=True,
        blank=True,
    )

    place = models.ForeignKey(
        "events.Place",
        on_delete=models.SET_NULL,
        verbose_name=_("place"),
        db_index=False,
        null=True,
        blank=True,
    )

    author = models.ForeignKey(
        to="accounts.User",
        on_delete=models.SET_NULL,
        related_name="events",
        verbose_name=_("author"),
        db_index=False,
        null=True,
        blank=True,
    )

    section = models.ForeignKey(
        to="sections.Section",
        on_delete=models.CASCADE,
        related_name="events",
        verbose_name=_("ESN section"),
        help_text=_("Users from this section can join this event."),
        db_index=True,
    )

    def __str__(self):
        # return self.title
        return f"{self.title} - {self.start.date()}"

    def is_oc(self, user: User) -> bool:
        return self.organizers.filter(user=user).exists()

    def is_moc(self, user: User) -> bool:
        return self.organizers.filter(user=user, role=OrganizerRole.EVENT_LEADER).exists()

    def is_participant(self, user: User) -> bool:
        return self.participants.filter(user=user, role=ParticipantState.CONFIRMED).exists()

    def can_edit(self, user: User) -> bool:
        return self.is_moc(user) or self.author == user or user.is_superuser

    def can_see_participants(self, user: User) -> bool:
        return self.is_moc(user) or self.author == user or user.is_superuser

    class Meta:
        ordering = ["start"]
        verbose_name = _("event")
        verbose_name_plural = _("events")


__all__ = ["Event"]

# TODO hybrid registration, default user, only online (qr), offline registrations (counter, subtract from capacity)
