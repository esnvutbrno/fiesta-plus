from allauth.account.admin import EmailAddressAdmin
from allauth.account.models import EmailAddress
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import AccountsConfiguration, User, UserProfile
from ..plugins.admin import BaseChildConfigurationAdmin


@admin.register(AccountsConfiguration)
class AccountsConfigurationAdmin(BaseChildConfigurationAdmin):
    pass


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    change_form_template = "loginas/change_form.html"

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "username",
                    "password",
                    "state",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                )
            },
        ),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": ("groups", "user_permissions"),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined", "modified")}),
    )
    readonly_fields = ("modified",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "nationality", "gender")
    list_filter = (
        "user__memberships__section",
        "gender",
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
