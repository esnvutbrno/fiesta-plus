from django.contrib import admin
from polymorphic.admin import PolymorphicChildModelAdmin

from .models import ESNcardsConfiguration
from apps.plugins.models import BasePluginConfiguration


@admin.register(ESNcardsConfiguration)
class EsncardsConfigurationAdmin(PolymorphicChildModelAdmin):
    base_model = BasePluginConfiguration
    show_in_index = True
