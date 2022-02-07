from __future__ import annotations

from datetime import datetime
from typing import TypedDict

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from django_lifecycle import BEFORE_CREATE, BEFORE_SAVE, LifecycleModelMixin, hook

from apps.utils.models import BaseTimestampedModel


class ESNcardApplication(LifecycleModelMixin, BaseTimestampedModel):
    # copied from user
    first_name = models.CharField(
        verbose_name=_("first name"),
        max_length=150,
    )
    last_name = models.CharField(verbose_name=_("last name"), max_length=150)
    nationality = CountryField(verbose_name=_("nationality"))
    university = models.ForeignKey(
        "universities.University",
        on_delete=models.RESTRICT,
        verbose_name=_("university"),
    )

    # filled by user
    birth_date = models.DateField(verbose_name=_("birth date"))

    # related to request
    section = models.ForeignKey(
        "sections.Section",
        on_delete=models.RESTRICT,
        verbose_name=_("section"),
    )
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.RESTRICT,
        verbose_name=_("issuer"),
    )

    class State(TextChoices):
        CREATED = "created", _("Created")
        ACCEPTED = "accepted", _("Accepted")
        READY_TO_PICKUP = "ready", _("Ready to pickup")
        ISSUED = "issued", _("Issued")

        DECLINED = "declined", _("Declined")
        CANCELLED = "cancelled", _("Cancelled")

    state = models.TextField(
        max_length=16,
        choices=State.choices,
        default=State.CREATED,
    )

    history: list['HistoryRecord'] = models.JSONField(
        default=list,
        encoder=DjangoJSONEncoder,
    )

    class HistoryRecord(TypedDict):
        timestamp: datetime
        initial_state: ESNcardApplication.State | str
        final_state: ESNcardApplication.State | str

    class Meta:
        verbose_name = _("ESNcard application")
        verbose_name_plural = _("ESNcard applications")

    @hook(BEFORE_SAVE, when="state", has_changed=True)
    @hook(BEFORE_CREATE)
    def on_state_change(self):
        self.history.append(self.HistoryRecord(
            timestamp=datetime.now(),
            initial_state=self.initial_value('state'),
            final_state=self.state,
        ))


__all__ = ["ESNcardApplication"]
