from __future__ import annotations

from django.contrib import admin
from django.contrib.admin import ModelAdmin


class BaseRequestAdmin(ModelAdmin):
    list_display = ["responsible_section", "issuer", "state", "matched_by", "matched_at", "created"]

    date_hierarchy = "created"

    list_filter = [
        ("responsible_section", admin.RelatedOnlyFieldListFilter),
        ("responsible_section__country", admin.AllValuesFieldListFilter),
        "state",
    ]

    autocomplete_fields = ["issuer", "matched_by"]

    search_fields = [
        "issuer__username",
        "issuer__email",
        "issuer__last_name",
        "issuer__first_name",
        "responsible_section__name",
    ]
