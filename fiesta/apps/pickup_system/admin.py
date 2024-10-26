from __future__ import annotations

from django.contrib import admin

from ..fiestarequests.admin import BaseRequestAdmin, BaseRequestMatchAdmin
from ..plugins.admin import BaseChildConfigurationAdmin
from .models import PickupRequest, PickupRequestMatch, PickupSystemConfiguration


@admin.register(PickupSystemConfiguration)
class PickupSystemConfigurationAdmin(BaseChildConfigurationAdmin):
    show_in_index = True


@admin.register(PickupRequest)
class PickupRequestAdmin(BaseRequestAdmin):
    _d = BaseRequestAdmin.list_display[:]  # to get own copy
    _d.insert(_d.index("state"), "place")
    _d.insert(_d.index("state"), "time")
    list_display = _d


@admin.register(PickupRequestMatch)
class PickupRequestMatchAdmin(BaseRequestMatchAdmin):
    pass
