from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.utils.models import BaseModel
import datetime 
from django.http import HttpResponse

class Participant(BaseModel):
    created = models.DateTimeField(
        verbose_name=_("created at"),
        help_text=_("when the user placed the ordered (does not have to be paid)"),
    )

    user = models.ForeignKey(
        to="accounts.User",
        related_name="event_participants",
        on_delete=models.SET_NULL,
        null=True,
        db_index=True,
        verbose_name=_("user"),
    )

    event = models.ForeignKey(
        to="events.Event",
        on_delete=models.SET_NULL,
        related_name="event_participants",
        null=True,
        db_index=True,
        verbose_name=_("event"),
    )

    price = models.ForeignKey(
        to="events.PriceVariant",
        on_delete=models.SET_NULL,
        verbose_name=_("price"),
        related_name="participants",
        null=True,
        db_index=False,
    )
    
    
    class State(models.TextChoices):  # TODO do we need a state if we have an expiration date
        WAITING = "waiting", _("Waiting")
        CONFIRMED = "confirmed", _("Confirmed")
        DELETED = "deleted", _("Deleted")

    state = models.CharField(
        choices=State.choices,
        default=State.WAITING,
        verbose_name=_("state"),
        help_text=_("current state of the event"),
    )

    def __str__(self):
        return f"{self.user} - {self.event}"

    @classmethod
    def register_for_event(self, user, event, price):
        """
        Class method to handle registration for an event.
        """

        if self.objects.filter(event=event).count() >= event.capacity:
            return HttpResponse("This event is full.")


        if self.objects.filter(user=user, event=event).exists():
            return HttpResponse("You are already registered for this event.")

        if price is None:
            return HttpResponse("You can't register for this event yet.")


        self.objects.create(
            created=datetime.datetime.now(),
            user=user,
            event=event,
            price=price,
            state=self.State.WAITING
        )
        return HttpResponse("Successfully registered for this event.")
    
    class Meta:
        unique_together = (("event", "user"),)
        verbose_name = _("participant")
        verbose_name_plural = _("participants")
        ordering = ["created"]
        

__all__ = ["Participant"]

# TODO problematika ověřování lidí (QR check-in)
