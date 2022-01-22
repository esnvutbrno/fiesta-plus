from django.contrib import admin
from polymorphic.admin import PolymorphicChildModelAdmin

from .models import AccountsConfiguration
from apps.plugins.models import BasePluginConfiguration


@admin.register(AccountsConfiguration)
class AccountsConfigurationAdmin(PolymorphicChildModelAdmin):
    base_model = BasePluginConfiguration
    show_in_index = True
