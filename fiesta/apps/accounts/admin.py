from allauth.account.admin import EmailAddressAdmin
from allauth.account.models import EmailAddress
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
    list_display = ("user", "nationality")
    list_filter = (
        "user__memberships__section",
        ("nationality", admin.AllValuesFieldListFilter),
    )
    autocomplete_fields = ("user",)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "user",
                "home_university",
                "home_faculty__university",
            )
        )


admin.site.unregister(EmailAddress)


@admin.register(EmailAddress)
class FiestaEmailAddressAdmin(EmailAddressAdmin):
    ...  # to have it in accounts admin
