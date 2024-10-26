from __future__ import annotations

from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.utils.translation import gettext_lazy as _

from apps.fiestarequests.models.request import BaseRequestProtocol
from apps.fiestatables.views.tables import PreprocessQuerySetMixin
from apps.utils.admin.change_links_mixin import AdminChangeLinksMixin


class BaseRequestAdmin(PreprocessQuerySetMixin, AdminChangeLinksMixin, ModelAdmin):
    # https://github.com/gitaarik/django-admin-relation-links
    prefetch_related = ["issuer", "responsible_section", "match", "match__matcher"]

    list_display = ["issuer", "responsible_section", "state", "match_link", "created"]

    change_links = ["match"]

    date_hierarchy = "created"

    list_filter = [
        ("responsible_section", admin.RelatedOnlyFieldListFilter),
        ("responsible_section__country", admin.AllValuesFieldListFilter),
        "state",
    ]

    autocomplete_fields = ["issuer"]

    search_fields = [
        "issuer__username",
        "issuer__email",
        "issuer__last_name",
        "issuer__first_name",
        "responsible_section__name",
    ]

    @admin.action(description=_("Mark selected created requests as cancelled"))
    def make_cancelled(self, request, queryset):
        queryset.filter(
            state=BaseRequestProtocol.State.CREATED,
        ).update(
            state=BaseRequestProtocol.State.CANCELLED,
        )

    actions = [make_cancelled]


class BaseRequestMatchAdmin(AdminChangeLinksMixin, PreprocessQuerySetMixin, ModelAdmin):
    list_display = ["matcher", "responsible_section", "request_link", "note", "created"]

    list_display_links = ["matcher"]

    change_links = ["request"]

    date_hierarchy = "created"

    list_filter = [
        ("request__responsible_section", admin.RelatedOnlyFieldListFilter),
        ("request__responsible_section__country", admin.AllValuesFieldListFilter),
    ]

    autocomplete_fields = ["request", "matcher"]

    search_fields = [
        "request__issuer__username",
        "request__issuer__email",
        "request__issuer__last_name",
        "request__issuer__first_name",
        "matcher__username",
        "matcher__email",
        "matcher__last_name",
        "matcher__first_name",
        "request__responsible_section__name",
    ]

    @admin.display(description=_("Responsible section"))
    def responsible_section(self, obj):
        return obj.request.responsible_section
