from __future__ import annotations

from django.utils.translation import gettext_lazy as _
from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget

from apps.sections.models import SectionMembership


class RemoteModelSelectWidgetMixin:
    empty_label = _("Type to search...")

    def build_attrs(self, base_attrs, extra_attrs=None):
        """Add select2's tag attributes."""
        attrs: dict = super().build_attrs(base_attrs, extra_attrs=extra_attrs)
        default_attrs = {"x-data": "modelSelect($el)"}
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
    
class MultipleUserWidget(RemoteModelSelectWidgetMixin, ModelSelect2MultipleWidget):
    search_fields = [
        "first_name__icontains",
        "last_name__icontains",
        "username__icontains",
    ]

    @classmethod
    def label_from_instance(cls, user):
        return f"{user.full_name} ({user.username})"



class ActiveLocalMembersFromSectionWidget(UserWidget):
    def filter_queryset(self, request, term, queryset=None, **dependent_fields):
        queryset = (
            (queryset or self.get_queryset())
            .filter(
                memberships__section=request.in_space_of_section,
            )
            .filter(
                memberships__role__in=(
                    SectionMembership.Role.MEMBER,
                    SectionMembership.Role.ADMIN,
                    SectionMembership.Role.EDITOR,
                ),
            )
        )

        return super().filter_queryset(request, term, queryset, **dependent_fields)
    
class MultipleActiveLocalMembersFromSectionWidget(MultipleUserWidget):
    def filter_queryset(self, request, term, queryset=None, **dependent_fields):
        queryset = (
            (queryset or self.get_queryset())
            .filter(
                memberships__section=request.in_space_of_section,
            )
            .filter(
                memberships__role__in=(
                    SectionMembership.Role.MEMBER,
                    SectionMembership.Role.ADMIN,
                    SectionMembership.Role.EDITOR,
                ),
            )
        )

        return super().filter_queryset(request, term, queryset, **dependent_fields)
class PlaceWidget(RemoteModelSelectWidgetMixin, ModelSelect2Widget):
    search_fields = [
        "name__icontains",
    ]

    @classmethod
    def label_from_instance(cls, place):
        return f"{place.name} ({place.link})"

class UniversityWidget(RemoteModelSelectWidgetMixin, ModelSelect2Widget):
    search_fields = [
        "name__icontains",
        "abbr__icontains",
    ]

    @classmethod
    def label_from_instance(cls, university):
        return f"{university.name} ({university.abbr})"


class UniversityForCurrentUserWidget(UniversityWidget):
    def filter_queryset(self, request, term, queryset=None, **dependent_fields):
        queryset = (queryset or self.get_queryset()).filter(
            # TODO: filter state?
            university_sections__section__memberships__user=request.user,
        )

        return super().filter_queryset(request, term, queryset, **dependent_fields)


class FacultyWidget(RemoteModelSelectWidgetMixin, ModelSelect2Widget):
    search_fields = [
        "university__name__icontains",
        "name__icontains",
        "abbr__icontains",
    ]

    @classmethod
    def label_from_instance(cls, faculty):
        return f"{faculty.name} ({faculty.abbr}) - {UniversityWidget.label_from_instance(faculty.university)}"


class FacultyForCurrentUserWidget(FacultyWidget):
    def filter_queryset(self, request, term, queryset=None, **dependent_fields):
        queryset = (queryset or self.get_queryset()).filter(
            # TODO: filter state?
            university__university_sections__section__memberships__user=request.user,
        )

        return super().filter_queryset(request, term, queryset, **dependent_fields)
