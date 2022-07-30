from django.contrib import admin
from polymorphic.admin import PolymorphicChildModelAdmin

from apps.plugins.models import BasePluginConfiguration
from .models import ESNcardApplication, ESNcardsConfiguration


@admin.register(ESNcardsConfiguration)
class EsncardsConfigurationAdmin(PolymorphicChildModelAdmin):
    base_model = BasePluginConfiguration
    show_in_index = True


@admin.register(ESNcardApplication)
class ESNcardApplicationAdmin(admin.ModelAdmin):
    list_display = ["user", "section", "state", "created"]
    list_filter = ["section", "state"]
    raw_id_fields = ["user", "section"]
