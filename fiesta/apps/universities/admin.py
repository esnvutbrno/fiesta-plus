from django.contrib import admin

from apps.universities.models import Faculty, University


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    ...


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    ...
