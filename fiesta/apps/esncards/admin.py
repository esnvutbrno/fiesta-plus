from django.contrib import admin
from polymorphic.admin import PolymorphicChildModelAdmin

from .models import ESNcardApplication, ESNcardsConfiguration
from apps.plugins.models import BasePluginConfiguration


@admin.register(ESNcardsConfiguration)
class EsncardsConfigurationAdmin(PolymorphicChildModelAdmin):
    base_model = BasePluginConfiguration
    show_in_index = True


@admin.register(ESNcardApplication)
class ESNcardApplicationAdmin(admin.ModelAdmin):
    list_display = ["user", "section", "state", "created"]
    list_filter = ["section", "state"]
    raw_id_fields = ["user", "section"]
