from __future__ import annotations

from django.contrib import admin
from django.db.models import Prefetch
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.utils.translation import gettext_lazy as _

from ..plugins.admin import BaseChildConfigurationAdmin
from ..plugins.models import Plugin
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
    list_display = (
        "name",
        "country",
        "code",
        "space_slug",
        "all_universities",
        "all_plugins",
        "memberships_count",
        "system_state",
    )
    list_filter = (("country", admin.AllValuesFieldListFilter), "system_state")

    list_editable = ("system_state",)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related(
                "memberships",
                "universities",
                Prefetch("plugins", queryset=Plugin.objects.exclude(state=Plugin.State.DISABLED)),
            )
        )

    @admin.display(
        description=_("Plugins"),
    )
    def all_plugins(self, obj: Section):
        return format_html(
            "<ul>{}</ul>",
            format_html_join(
                "\n",
                "<li><a href='{}'>{}</a></li>",
                (
                    (
                        reverse("admin:plugins_plugin_change", args=(p.pk,)),
                        p,
                    )
                    for p in obj.plugins.all()
                ),
            ),
        )

    @admin.display(
        description=_("Memberships"),
    )
    def memberships_count(self, obj: Section):
        return obj.memberships.count()

    @admin.display(
        description=_("Universities"),
    )
    def all_universities(self, obj: Section):
        return format_html(
            "<ul>{}</ul>",
            format_html_join(
                "\n",
                "<li>{}</li>",
                ((p,) for p in obj.universities.all()),
            ),
        )

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
        "user__profile__faculty__name",
        "user__profile__faculty__university__name",
        "user__profile__university__name",
        "section__name",
        "section__universities__name",
    )
