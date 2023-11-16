from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from apps.fiestarequests.models import BaseRequestSystemConfiguration


class PickupSystemConfiguration(BaseRequestSystemConfiguration):
    ...

    class Meta:
        verbose_name = _("pickup system configuration")
        verbose_name_plural = _("pickup system configurations")


__all__ = ["PickupSystemConfiguration"]
