from __future__ import annotations

import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _
from location_field.models.plain import PlainLocationField

from apps.fiestarequests.models import BaseRequestSystemConfiguration


class PickupSystemConfiguration(BaseRequestSystemConfiguration):
    default_pickup_location = PlainLocationField(
        verbose_name=_("default pickup location"),
        blank=True,
        null=True,
        zoom=4,
        # some random location in Brno
        default="49.194791469587045,16.608590483447188",
        help_text=_("This location will be used as a default pickup location displayed for new pickup requests."),
    )

    email_notify_on_match = models.BooleanField(
        default=True,
        verbose_name=_("Send email notifications on match"),
    )
    email_notify_issuer_delay = models.DurationField(
        default=datetime.timedelta(hours=1),
        verbose_name=_("Delay before notifying the issuer"),
        help_text=_("Gives editors time to correct the match before the student is notified."),
    )

    class Meta:
        verbose_name = _("pickup system configuration")
        verbose_name_plural = _("pickup system configurations")


__all__ = ["PickupSystemConfiguration"]
