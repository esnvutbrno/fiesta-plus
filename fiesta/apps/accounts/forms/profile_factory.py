from __future__ import annotations

from django.db.models import Field
from django.forms import Field as FormField, modelform_factory

from apps.accounts.forms.profile import UserProfileForm
from apps.accounts.models import User, UserProfile
from apps.sections.models import SectionMembership, SectionsConfiguration


class UserProfileFormFactory:
    """
    Creates UserProfileForm dynamically for specific user -- based on all SectionsConfiguration related to specific user.
    """

    FIELDS_TO_CONFIGURATION = {
        UserProfile.university: SectionsConfiguration.required_university,
        UserProfile.faculty: SectionsConfiguration.required_faculty,
        UserProfile.nationality: SectionsConfiguration.required_nationality,
        UserProfile.gender: SectionsConfiguration.required_gender,
        UserProfile.picture: SectionsConfiguration.required_picture,
        UserProfile.phone_number: SectionsConfiguration.required_phone_number,
        UserProfile.interests: SectionsConfiguration.required_interests,
    }
    _FIELD_NAMES_TO_CONFIGURATION = {f.field.name: conf_field for f, conf_field in FIELDS_TO_CONFIGURATION.items()}

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
        base_form_class: type[UserProfileForm] = UserProfileForm,
    ) -> type[UserProfileForm]:
        """
        Creates the profile form class for specific user.
        Fields and configuration are constructed from all SectionsConfiguration from
        all sections from all memberships of that specific user.
        """
        confs = cls.get_user_configuration(user)

        def callback(f: Field, **kwargs) -> FormField:
            # TODO: what to do, when no specific configuration is found?

            if conf_field := cls._FIELD_NAMES_TO_CONFIGURATION.get(f.name):
                return f.formfield(required=any(conf_field.__get__(c) for c in confs), **kwargs)
            return f.formfield(**kwargs)

        return modelform_factory(
            model=UserProfile,
            form=base_form_class,
            fields=cls.get_form_fields(user),
            formfield_callback=callback,
        )

    @classmethod
    def get_form_fields(cls, user: User):
        confs = cls.get_user_configuration(user)
        # TODO: what to do, when no specific configuration is found?

        fields_to_include = tuple(
            field_name
            for field_name, conf_field in cls._FIELD_NAMES_TO_CONFIGURATION.items()
            if any(conf_field.__get__(c) is not None for c in confs)
        )
        all_fields = fields_to_include + UserProfileForm.Meta.fields
        # first all required fields, after them all the rest in original order
        return sorted(
            set(all_fields),
            key=lambda f: (not ((field := UserProfileForm.base_fields.get(f)) and field.required), all_fields.index(f)),
        )
