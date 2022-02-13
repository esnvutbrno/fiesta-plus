from __future__ import annotations

from typing import Type

from django.db.models import Field
from django.forms import HiddenInput, modelform_factory, Field as FormField

from apps.accounts.models import UserProfile, AccountsConfiguration
from apps.fiestaforms.forms import BaseModelForm


class UserProfileForm(BaseModelForm):
    # title = _("Application Form")

    @classmethod
    def from_accounts_configuration(cls, conf: AccountsConfiguration) -> Type[UserProfileForm]:
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
