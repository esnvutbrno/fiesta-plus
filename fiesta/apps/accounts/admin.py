from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from polymorphic.admin import PolymorphicChildModelAdmin

from .models import AccountsConfiguration, User, UserProfile
from apps.plugins.models import BasePluginConfiguration


@admin.register(AccountsConfiguration)
class AccountsConfigurationAdmin(PolymorphicChildModelAdmin):
    base_model = BasePluginConfiguration
    show_in_index = True


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + ((None, {"fields": ("state",)}),)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    ...
