from __future__ import annotations

from datetime import UTC, datetime

from django.db import models
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField

from apps.accounts.models import User
from apps.utils.models import BaseModel


class EventPriceVariantType(TextChoices):
    FREE = "free", _("Free")
    STANDARD = "standard", _("Standard")
    WITH_ESN_CARD = "with_esn_card", _("With ESN card")

    def is_available(self, variant: PriceVariant, user: User):
        to_ = variant.available_to
        from_ = variant.available_from

        if from_ is not None and from_ != "" and from_ < datetime.now(UTC):
            return False

        if to_ is not None and to_ != "" and to_ > datetime.now(UTC):
            return False

        if variant.type == self.STANDARD or (
            variant.type == self.WITH_ESN_CARD
            and user.profile_or_none is not None
            and user.profile.is_esn_card_holder()
        ):
            return True

        return False


class PriceVariant(BaseModel):
    title = models.CharField(
        max_length=256,
        verbose_name=_("title"),
        help_text=_("full name of the price"),
    )

    type = models.CharField(
        max_length=255,
        choices=EventPriceVariantType.choices,
        verbose_name=_("type"),
    )

    amount = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency="CZK",
        verbose_name=_("amount"),
    )

    event = models.ForeignKey(
        "events.Event",
        related_name="price_variant",
        on_delete=models.CASCADE,
        verbose_name=_("event"),
        null=True,
        db_index=True,
    )

    available_from = models.DateTimeField(
        verbose_name=_("available from"),
        help_text=_("From when users can purchase for this price."),
        null=True,
        blank=True,
    )

    available_to = models.DateTimeField(
        verbose_name=_("available to"),
        help_text=_("Until when users can purchase for this price."),
        null=True,
        blank=True,
    )

    data = models.JSONField(
        verbose_name=_("data"),
        help_text=_("any data related to the price"),
        default=dict,
    )

    class Meta:
        unique_together = (("title", "event"),)
        verbose_name = _("price variant")
        verbose_name_plural = _("price variants")


__all__ = ["PriceVariant"]
