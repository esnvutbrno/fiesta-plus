from django.contrib import admin

from .models import BuddySystemConfiguration, BuddyRequest
from ..fiestarequests.admin import BaseRequestAdmin
from ..plugins.admin import BaseChildConfigurationAdmin


@admin.register(BuddySystemConfiguration)
class BuddySystemConfigurationAdmin(BaseChildConfigurationAdmin):
    # TODO: parent admin doesn't work with inserted middle abstract class BaseRequestSystemConfiguration
    show_in_index = True


@admin.register(BuddyRequest)
class BuddyRequestAdmin(BaseRequestAdmin):
    pass
