from __future__ import annotations

from typing import Type

from django.db.models import Field
from django.forms import Field as FormField, modelform_factory
from django.utils.translation import gettext_lazy as _
from django_select2.forms import ModelSelect2Widget

from apps.accounts.models import User, UserProfile
from apps.fiestaforms.forms import BaseModelForm
from apps.sections.models import SectionsConfiguration


class ChoicesJsWidgetMixin:
    def build_attrs(self, base_attrs, extra_attrs=None):
        """Add select2's tag attributes."""
        attrs: dict = super().build_attrs(base_attrs, extra_attrs=extra_attrs)
        default_attrs = {
            "x-data": f"modelSelect($refs.{attrs.get('id')})",
            "x-ref": attrs.get('id')
        }
        attrs.update(default_attrs)
        return attrs

    @property
    def media(self):
        return None


class UniversityWidget(ChoicesJsWidgetMixin, ModelSelect2Widget):
    search_fields = [
        "name__icontains",
        "abbr__icontains",
    ]


class FacultyWidget(ChoicesJsWidgetMixin, ModelSelect2Widget):
    search_fields = [
        "name__icontains",
        "abbr__icontains",
    ]


class UserProfileForm(BaseModelForm):
    FIELDS_TO_CONFIGURATION = {
        UserProfile.nationality: SectionsConfiguration.required_nationality,
        UserProfile.gender: SectionsConfiguration.required_gender,
        UserProfile.picture: SectionsConfiguration.required_picture,
    }
    _FIELD_NAMES_TO_CONFIGURATION = {
        f.field.name: conf_field for f, conf_field in FIELDS_TO_CONFIGURATION.items()
    }

    @classmethod
    def for_user(
        cls,
        user: User,
    ) -> Type[UserProfileForm]:
        """
        Creates the profile form class for specific user.
        Fields and configuration are constructed from all AccountsConfigurations from
        all sections from all memberships of that specific user.
        """
        confs = SectionsConfiguration.objects.filter(
            plugin__section__memberships__user=user,
            # TODO: check also Membership.state?
        )

        def callback(f: Field, **kwargs) -> FormField:
            if conf_field := cls._FIELD_NAMES_TO_CONFIGURATION.get(f.name):
                return f.formfield(
                    required=any(conf_field.__get__(c) for c in confs), **kwargs
                )
            return f.formfield(**kwargs)

        fields_to_include = tuple(
            field_name
            for field_name, conf_field in cls._FIELD_NAMES_TO_CONFIGURATION.items()
            if any(conf_field.__get__(c) is not None for c in confs)
        )

        form_klass = modelform_factory(
            model=UserProfile,
            form=cls,
            fields=cls.Meta.fields + fields_to_include,
            formfield_callback=callback,
        )

        return form_klass

    class Meta:
        model = UserProfile

        fields = (
            # TODO: think about limiting the choices by country of section, in which is current membership
            "home_university",
            "home_faculty",
            "guest_faculty",
            "picture",
        )

        widgets = {
            "home_university": UniversityWidget,
            "home_faculty": FacultyWidget,
            "guest_faculty": FacultyWidget,
        }


class UserProfileFinishForm(UserProfileForm):
    submit_text = _("Finish Profile")
