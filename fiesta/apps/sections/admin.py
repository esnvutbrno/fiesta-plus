from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from polymorphic.admin import PolymorphicChildModelAdmin

from .models import Section, SectionMembership, SectionsConfiguration, SectionUniversity
from apps.plugins.models import BasePluginConfiguration


@admin.register(SectionsConfiguration)
class SectionsConfigurationAdmin(PolymorphicChildModelAdmin):
    base_model = BasePluginConfiguration
    show_in_index = True


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "all_universities")
    list_filter = (("country", admin.AllValuesFieldListFilter),)

    @admin.display(
        description=_("Universities"),
    )
    def all_universities(self, obj: Section):
        return ", ".join(map(str, obj.universities.all()))

    class SectionUniversityInline(admin.StackedInline):
        model = SectionUniversity

    inlines = (SectionUniversityInline,)


@admin.register(SectionMembership)
class SectionMembershipAdmin(admin.ModelAdmin):
    list_display = ("section", "user", "role", "state")
    list_filter = ("section", "role", "state")
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
