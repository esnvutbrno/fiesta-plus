from __future__ import annotations

from django.contrib import admin

from ..fiestarequests.admin import BaseRequestAdmin, BaseRequestMatchAdmin
from ..plugins.admin import BaseChildConfigurationAdmin
from .models import BuddyRequest, BuddyRequestMatch, BuddySystemConfiguration


@admin.register(BuddySystemConfiguration)
class BuddySystemConfigurationAdmin(BaseChildConfigurationAdmin):
    show_in_index = True


@admin.register(BuddyRequest)
class BuddyRequestAdmin(BaseRequestAdmin):
    pass


@admin.register(BuddyRequestMatch)
class BuddyRequestMatchAdmin(BaseRequestMatchAdmin):
    pass
