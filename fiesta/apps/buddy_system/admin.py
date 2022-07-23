from django.contrib import admin
from polymorphic.admin import PolymorphicChildModelAdmin

from apps.plugins.models import BasePluginConfiguration
from .models import BuddySystemConfiguration


@admin.register(BuddySystemConfiguration)
class BuddySystemConfigurationAdmin(PolymorphicChildModelAdmin):
    base_model = BasePluginConfiguration
    show_in_index = True
