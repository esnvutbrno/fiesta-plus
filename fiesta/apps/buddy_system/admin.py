from django.contrib import admin

from ..fiestarequests.admin import BaseRequestAdmin
from ..plugins.admin import BaseChildConfigurationAdmin
from .models import BuddyRequest, BuddySystemConfiguration


@admin.register(BuddySystemConfiguration)
class BuddySystemConfigurationAdmin(BaseChildConfigurationAdmin):
    show_in_index = True


@admin.register(BuddyRequest)
class BuddyRequestAdmin(BaseRequestAdmin):
    pass
