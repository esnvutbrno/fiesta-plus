from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.utils.models import BaseModel


class Price(BaseModel):
    title = models.CharField(
        max_length=64,
        unique=True,
        verbose_name=_("title"),
        help_text=_("full name of the price"),
    )

    description = models.TextField(
        verbose_name=_("description"),
        help_text=_("short description of the price"),
    )

    # currency # TODO jak?

    amounts = models.IntegerField(
        verbose_name=_("amount"),
        help_text=_("the price itself"),
    )

    esn_card_only = models.BooleanField(
        verbose_name=_("amount"),
        help_text=_("whether the price is available only with ESN card"),
    )

    section = models.ManyToManyRel(  # TODO authorisation
        related_name="event",
    )

    def __str__(self):
        return self.title


__all__ = ["Price"]
