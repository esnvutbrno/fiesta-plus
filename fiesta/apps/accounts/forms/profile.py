from __future__ import annotations

from django.db.models import Field
from django.forms import Field as FormField, fields_for_model, modelform_factory
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User, UserProfile
from apps.fiestaforms.fields.array import ChoicedArrayField
from apps.fiestaforms.forms import BaseModelForm
from apps.fiestaforms.widgets.models import FacultyWidget, UniversityWidget
from apps.sections.models import SectionMembership, SectionsConfiguration

FIELDS_FROM_USER = ("first_name", "last_name")
REQUIRED_FIELDS_FROM_USER = FIELDS_FROM_USER


def _create_user_fields():
    fields = fields_for_model(
        User,
        fields=FIELDS_FROM_USER,
    )
    for f in REQUIRED_FIELDS_FROM_USER:
        fields[f].required = True
    return fields


USER_FIELDS = _create_user_fields()


class UserProfileForm(BaseModelForm):
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
    def get_form_fields(cls, user: User):
        confs = cls.get_user_configuration(user)
        # TODO: what to do, when no specific configuration is found?

        fields_to_include = tuple(
            field_name
            for field_name, conf_field in cls._FIELD_NAMES_TO_CONFIGURATION.items()
            if any(conf_field.__get__(c) is not None for c in confs)
        )
        all_fields = fields_to_include + cls.Meta.fields
        # first all required fields, after them all the rest in original order
        return sorted(
            set(all_fields),
            key=lambda f: (not ((field := UserProfileForm.base_fields.get(f)) and field.required), all_fields.index(f)),
        )

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
        confs = cls.get_user_configuration(user)

        def callback(f: Field, **kwargs) -> FormField:
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

    # include pre-generated field from User
    locals().update(USER_FIELDS)

    class Meta:
        model = UserProfile

        field_classes = {
            "interests": ChoicedArrayField,
        }

        # fields, which are shown independently on section configurations
        fields = (
            *USER_FIELDS.keys(),
            # TODO: think about limiting the choices by country of section, in which is current membership
            "university",
            "faculty",
            "picture",
            "facebook",
            "instagram",
            "telegram",
            "whatsapp",
            "interests",
        )

        widgets = {
            "university": UniversityWidget,
            "faculty": FacultyWidget,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            user: User | None = self.instance and self.instance.user
        except User.DoesNotExist:
            user = None

        if user:
            for f in USER_FIELDS:
                self.initial[f] = getattr(user, f, None)

    def save(self, commit=True):
        # first save user fields, since validation in UserProfile.save() could fail and we've to submit the form again
        for f in USER_FIELDS:
            setattr(self.instance.user, f, self.cleaned_data.get(f))
        self.instance.user.save(update_fields=USER_FIELDS.keys())

        return super().save(commit=commit)


class UserProfileFinishForm(UserProfileForm):
    submit_text = _("Finish Profile")
