from __future__ import annotations

from django.db import models
from django.db.models import DateTimeField
from django.utils.translation import gettext_lazy as _
from location_field.models.plain import PlainLocationField

from apps.fiestarequests.models import base_request_model_factory

BaseRequestForPickupSystem, BaseRequestMatchForPickupSystem = base_request_model_factory(
    final_request_model_name="pickup_system.PickupRequest",
    related_base="pickup_system",
    url_namespace="pickup_system",
)


class PickupRequest(BaseRequestForPickupSystem):
    time = DateTimeField(
        verbose_name=_("pickup time"),
    )
    place = models.CharField(
        verbose_name=_("pickup place name"),
        max_length=256,
    )
    location = PlainLocationField(
        verbose_name=_("pickup point"),
        based_fields=["pickup_place"],
        default="49.1922443,16.6113382",
        zoom=4,
    )

    class Meta(BaseRequestForPickupSystem.Meta):
        verbose_name = _("pickup request")
        verbose_name_plural = _("pickup requests")

    def __str__(self):
        return f"Pickup Request {self.issuer}: {self.get_state_display()}"

    @property
    def location_as_google_maps_link(self):
        return f"https://www.google.com/maps/place/{self.location}?zoom=15"
        # return f"https://www.google.com/maps/search/?api=1&query={self.location}"


class PickupRequestMatch(BaseRequestMatchForPickupSystem):
    class Meta(BaseRequestForPickupSystem.Meta):
        verbose_name = _("pickup request match")
        verbose_name_plural = _("pickup request matches")

    def __str__(self):
        return f"Pickup Request Match {self.matcher}: {self.request}"
