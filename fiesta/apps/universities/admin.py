from __future__ import annotations

from django.contrib import admin

from apps.universities.models import Faculty, University


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ["name", "abbr", "country"]
    list_filter = (("country", admin.AllValuesFieldListFilter),)


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ["name", "abbr", "university"]
    list_filter = ["university"]
