from __future__ import annotations

from django.forms import fields_for_model
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User, UserProfile
from apps.fiestaforms.fields.array import ChoicedArrayField
from apps.fiestaforms.forms import BaseModelForm
from apps.fiestaforms.widgets.models import FacultyWidget, UniversityWidget

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


FORM_FIELDS_FROM_USER = _create_user_fields()


class UserProfileForm(BaseModelForm):
    # include pre-generated field from User
    locals().update(FORM_FIELDS_FROM_USER)

    class Meta:
        model = UserProfile

        field_classes = {
            "interests": ChoicedArrayField,
        }

        # fields, which are shown independently on section configurations
        fields = (
            *FORM_FIELDS_FROM_USER.keys(),
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
            for f in FORM_FIELDS_FROM_USER:
                self.initial[f] = getattr(user, f, None)

    def save(self, commit=True):
        # first save user fields, since validation in UserProfile.save() could fail and we've to submit the form again
        for f in FORM_FIELDS_FROM_USER:
            setattr(self.instance.user, f, self.cleaned_data.get(f))
        self.instance.user.save(update_fields=FORM_FIELDS_FROM_USER.keys())

        return super().save(commit=commit)


class UserProfileFinishForm(UserProfileForm):
    submit_text = _("Finish Profile")
