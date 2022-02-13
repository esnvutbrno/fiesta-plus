from __future__ import annotations

from typing import Type

from django.db.models import Field
from django.forms import Field as FormField, HiddenInput, modelform_factory

from apps.accounts.models import AccountsConfiguration, UserProfile
from apps.fiestaforms.forms import BaseModelForm


class UserProfileForm(BaseModelForm):
    # title = _("Application Form")

    @classmethod
    def from_accounts_configuration(
        cls, conf: AccountsConfiguration
    ) -> Type[UserProfileForm]:
        # TODO: find generic way for configuration instance -> form setup
        include_nationality = conf.required_nationality is not None

        def callback(f: Field, **kwargs) -> FormField:
            if f.name == "nationality":
                return f.formfield(required=conf.required_nationality, **kwargs)
            return f.formfield(**kwargs)

        form_klass = modelform_factory(
            model=UserProfile,
            form=cls,
            fields=cls.Meta.fields + (("nationality",) if include_nationality else ()),
            formfield_callback=callback,
        )

        return form_klass

    class Meta:
        model = UserProfile

        fields = (
            "user",
            "home_university",
            "guest_faculty",
        )

        widgets = {
            "user": HiddenInput,
        }
