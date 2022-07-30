from __future__ import annotations

from django.utils.translation import gettext_lazy as _
from django_select2.forms import ModelSelect2Widget


class RemoteModelSelectWidgetMixin:
    empty_label = _("Type to search...")

    def build_attrs(self, base_attrs, extra_attrs=None):
        """Add select2's tag attributes."""
        attrs: dict = super().build_attrs(base_attrs, extra_attrs=extra_attrs)
        default_attrs = {
            "x-data": "modelSelect($el)",
        }
        attrs.update(default_attrs)
        return attrs

    @property
    def media(self):
        return None


class UserWidget(RemoteModelSelectWidgetMixin, ModelSelect2Widget):
    search_fields = [
        "first_name__icontains",
        "last_name__icontains",
        "username__icontains",
    ]

    @classmethod
    def label_from_instance(cls, user):
        return f"{user.full_name} ({user.username})"


class UniversityWidget(RemoteModelSelectWidgetMixin, ModelSelect2Widget):
    search_fields = [
        "name__icontains",
        "abbr__icontains",
    ]

    @classmethod
    def label_from_instance(cls, university):
        return f"{university.name} ({university.abbr})"


class FacultyWidget(RemoteModelSelectWidgetMixin, ModelSelect2Widget):
    search_fields = [
        "university__name__icontains",
        "name__icontains",
        "abbr__icontains",
    ]

    @classmethod
    def label_from_instance(cls, faculty):
        return f"{faculty.name} ({faculty.abbr}) - {UniversityWidget.label_from_instance(faculty.university)}"
