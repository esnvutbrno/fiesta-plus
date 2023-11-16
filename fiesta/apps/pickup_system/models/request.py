from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from apps.fiestarequests.models import base_request_model_factory

BaseRequestForPickupSystem, BaseRequestMatchForPickupSystem = base_request_model_factory(
    final_request_model_name="pickup_system.PickupRequest",
    related_base="pickup_system",
)


class PickupRequest(BaseRequestForPickupSystem):
    # TODO: date/time/place

    class Meta(BaseRequestForPickupSystem.Meta):
        verbose_name = _("pickup request")
        verbose_name_plural = _("pickup requests")

    def __str__(self):
        return f"Pickup Request {self.issuer}: {self.get_state_display()}"


class PickupRequestMatch(BaseRequestMatchForPickupSystem):
    class Meta(BaseRequestForPickupSystem.Meta):
        verbose_name = _("pickup request match")
        verbose_name_plural = _("pickup request matches")

    def __str__(self):
        return f"Pickup Request Match {self.matcher}: {self.request}"
