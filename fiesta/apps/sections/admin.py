from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ..plugins.admin import BaseChildConfigurationAdmin
from .models import Section, SectionMembership, SectionsConfiguration, SectionUniversity


@admin.register(SectionsConfiguration)
class SectionsConfigurationAdmin(BaseChildConfigurationAdmin):
    list_editable = [
        "required_nationality",
        "required_gender",
        "required_picture",
        "required_interests",
        "auto_approved_membership_for_international",
    ]
    list_display = BaseChildConfigurationAdmin.list_display + list_editable


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "space_slug", "all_universities", "system_state")
    list_filter = (("country", admin.AllValuesFieldListFilter), "system_state")

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("memberships", "universities")

    @admin.display(
        description=_("Universities"),
    )
    def all_universities(self, obj: Section):
        return ", ".join(map(str, obj.universities.all()))

    class SectionUniversityInline(admin.StackedInline):
        model = SectionUniversity
        extra = 1

    # TODO: Listing all memberships in section admin
    #  is kinda slow, so usage of some paginated would be useful
    class SectionMembershipInline(admin.TabularInline):
        model = SectionMembership
        autocomplete_fields = ("user",)
        extra = 1

        def get_queryset(self, request):
            return super().get_queryset(request).select_related("section", "user").order_by("-role", "user__username")

    inlines = (
        # SectionMembershipInline,
        SectionUniversityInline,
    )


@admin.register(SectionMembership)
class SectionMembershipAdmin(admin.ModelAdmin):
    list_display = ("section", "user", "role", "state", "created")
    list_filter = ("section", "role", "state", "user__state")
    list_editable = ("role", "state")
    autocomplete_fields = ("user",)
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__profile__home_faculty__name",
        "user__profile__home_faculty__university__name",
        "user__profile__home_university__name",
        "user__profile__guest_faculty__university__name",
        "section__name",
        "section__universities__name",
    )
