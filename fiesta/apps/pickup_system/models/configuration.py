from __future__ import annotations

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

    class Meta:
        verbose_name = _("pickup system configuration")
        verbose_name_plural = _("pickup system configurations")


__all__ = ["PickupSystemConfiguration"]
