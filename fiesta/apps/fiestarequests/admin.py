from django.contrib import admin
from django.contrib.admin import ModelAdmin


class BaseRequestAdmin(ModelAdmin):
    list_display = ["responsible_section", "issuer", "state", "matched_by"]

    date_hierarchy = "created"

    list_filter = [
        ("responsible_section__country", admin.AllValuesFieldListFilter),
        "state",
    ]

    autocomplete_fields = ["issuer", "matched_by"]
