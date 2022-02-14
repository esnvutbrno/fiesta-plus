from __future__ import annotations

from typing import Type

from django.db.models import Field
from django.forms import Field as FormField, modelform_factory

from apps.accounts.models import AccountsConfiguration, User, UserProfile
from apps.fiestaforms.forms import BaseModelForm


class UserProfileForm(BaseModelForm):
    # title = _("Application Form")

    FIELDS_TO_CONFIGURATION = {
        UserProfile.nationality: AccountsConfiguration.required_nationality,
        UserProfile.gender: AccountsConfiguration.required_gender,
    }
    FIELD_NAMES_TO_CONFIGURATION = {
        f.field.name: conf_field for f, conf_field in FIELDS_TO_CONFIGURATION.items()
    }

    @classmethod
    def for_user(
        cls,
        user: User,
    ) -> Type[UserProfileForm]:
        confs = AccountsConfiguration.objects.filter(
            plugin__section__memberships__user=user,
            # TODO: check also Membership.state?
        )

        def callback(f: Field, **kwargs) -> FormField:
            if conf_field := cls.FIELD_NAMES_TO_CONFIGURATION.get(f.name):
                return f.formfield(
                    required=any(conf_field.__get__(c) for c in confs), **kwargs
                )
            return f.formfield(**kwargs)

        fields_to_include = tuple(
            field_name
            for field_name, conf_field in cls.FIELD_NAMES_TO_CONFIGURATION.items()
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
            "home_university",
            "guest_faculty",
        )
