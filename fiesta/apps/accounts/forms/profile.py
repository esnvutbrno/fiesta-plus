from __future__ import annotations

from django.db.models import Field
from django.forms import Field as FormField, modelform_factory
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User, UserProfile
from apps.fiestaforms.fields.array import ChoicedArrayField
from apps.fiestaforms.forms import BaseModelForm
from apps.fiestaforms.widgets.models import FacultyWidget, UniversityWidget
from apps.sections.models import SectionMembership, SectionsConfiguration


class UserProfileForm(BaseModelForm):
    FIELDS_TO_CONFIGURATION = {
        UserProfile.nationality: SectionsConfiguration.required_nationality,
        UserProfile.gender: SectionsConfiguration.required_gender,
        UserProfile.picture: SectionsConfiguration.required_picture,
        UserProfile.phone_number: SectionsConfiguration.required_phone_number,
        UserProfile.interests: SectionsConfiguration.required_interests,
    }
    _FIELD_NAMES_TO_CONFIGURATION = {f.field.name: conf_field for f, conf_field in FIELDS_TO_CONFIGURATION.items()}

    @classmethod
    def get_form_fields(cls, user: User):
        confs = cls.get_user_configuration(user)
        # TODO: what to do, when no specific configuration is found?

        fields_to_include = tuple(
            field_name
            for field_name, conf_field in cls._FIELD_NAMES_TO_CONFIGURATION.items()
            if any(conf_field.__get__(c) is not None for c in confs)
        )
        return cls.Meta.fields + fields_to_include

    @classmethod
    def get_user_configuration(cls, user: User):
        # all related configurations
        return SectionsConfiguration.objects.filter(
            # from all user's memberships sections
            plugins__section__memberships__in=user.memberships.filter(
                # with waiting for confirmation or already active membership
                state__in=(
                    SectionMembership.State.UNCONFIRMED,  # waiting for confirmation
                    SectionMembership.State.ACTIVE,  # already active, need to have a valid profile
                )
            )
        )

    @classmethod
    def for_user(
            cls,
            user: User,
    ) -> type[UserProfileForm]:
        """
        Creates the profile form class for specific user.
        Fields and configuration are constructed from all SectionsConfiguration from
        all sections from all memberships of that specific user.
        """

        def callback(f: Field, **kwargs) -> FormField:
            confs = cls.get_user_configuration(user)
            # TODO: what to do, when no specific configuration is found?

            if conf_field := cls._FIELD_NAMES_TO_CONFIGURATION.get(f.name):
                return f.formfield(required=any(conf_field.__get__(c) for c in confs), **kwargs)
            return f.formfield(**kwargs)

        return modelform_factory(
            model=UserProfile,
            form=cls,
            fields=cls.get_form_fields(user),
            formfield_callback=callback,
        )

    class Meta:
        model = UserProfile

        field_classes = {
            "interests": ChoicedArrayField,
        }

        fields = (
            # TODO: think about limiting the choices by country of section, in which is current membership
            "home_university",
            "home_faculty",
            "guest_faculty",
            "picture",
            "facebook",
            "instagram",
            "telegram",
            "whatsapp",
            "interests",
        )

        widgets = {
            "home_university": UniversityWidget,
            "home_faculty": FacultyWidget,
            "guest_faculty": FacultyWidget,
        }


class UserProfileFinishForm(UserProfileForm):
    submit_text = _("Finish Profile")
