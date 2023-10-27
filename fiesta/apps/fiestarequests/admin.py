from __future__ import annotations

from django.contrib import admin
from django.contrib.admin import ModelAdmin


class BaseRequestAdmin(ModelAdmin):
    # https://github.com/gitaarik/django-admin-relation-links

    list_display = ["responsible_section", "issuer", "state", "match", "created"]

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


class BaseRequestMatchAdmin(ModelAdmin):
    list_display = ["matcher", "note", "created"]

    date_hierarchy = "created"

    list_filter = [
        ("request__responsible_section", admin.RelatedOnlyFieldListFilter),
        ("request__responsible_section__country", admin.AllValuesFieldListFilter),
    ]

    autocomplete_fields = ["matcher"]

    search_fields = [
        "request__issuer__username",
        "request__issuer__email",
        "request__issuer__last_name",
        "request__issuer__first_name",
        "matcher__username",
        "matcher__email",
        "matcher__last_name",
        "matcher__first_name",
        "request_match__responsible_section__name",
    ]
