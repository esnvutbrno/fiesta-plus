from __future__ import annotations

from allauth.account.admin import EmailAddressAdmin
from allauth.account.models import EmailAddress
from django.contrib import admin
from django.contrib.admin import display
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from .models import User, UserProfile


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
    list_display = DjangoUserAdmin.list_display + ("memberships",)

    @display
    def memberships(self, obj):
        return ", ".join(f"{s.section.name}: {s.role}" for s in obj.memberships.all())

    def get_queryset(self, request):
        qs: QuerySet = super().get_queryset(request)

        return qs.prefetch_related("memberships__section")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "nationality", "gender", "picture")
    list_filter = (
        "user__memberships__section",
        "gender",
        ("nationality", admin.AllValuesFieldListFilter),
    )
    autocomplete_fields = ("user",)
    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
    ]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "user",
                "university",
                "faculty__university",
            )
        )


admin.site.unregister(EmailAddress)


@admin.register(EmailAddress)
class FiestaEmailAddressAdmin(EmailAddressAdmin):
    ...  # to have it in accounts admin
