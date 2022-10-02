from django.contrib import admin
from django.contrib.admin import ModelAdmin


class BaseRequestAdmin(ModelAdmin):
    list_display = ["responsible_section", "issuer", "state", "matched_by", "created"]

    date_hierarchy = "created"

    list_filter = [
        ("responsible_section", admin.RelatedOnlyFieldListFilter),
        ("responsible_section__country", admin.AllValuesFieldListFilter),
        "state",
    ]

    autocomplete_fields = ["issuer", "matched_by"]

    search_fields = ["issuer__username", "issuer__email", "responsible_section__name"]
