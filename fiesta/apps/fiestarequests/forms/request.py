from __future__ import annotations

from django.forms import BooleanField, Textarea, fields_for_model
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import UserProfile
from apps.fiestaforms.forms import BaseModelForm
from apps.fiestaforms.widgets.models import FacultyForCurrentUserWidget

USER_PROFILE_CONTACT_FIELDS = fields_for_model(
    UserProfile,
    fields=("facebook", "instagram", "telegram", "whatsapp"),
)


class BaseNewRequestForm(BaseModelForm):
    submit_text = _("Send request for buddy")

    # TODO: group field somehow and add group headings
    facebook, instagram, telegram, whatsapp = USER_PROFILE_CONTACT_FIELDS.values()

    approving_request = BooleanField(required=True)

    class Meta:
        fields = (
            "note",
            "issuer_faculty",
        )
        field_classes = {}
        widgets = {
            "issuer_faculty": FacultyForCurrentUserWidget,
            "note": Textarea(attrs={"rows": 5}),
        }
        labels = {
            "note": _("Tell us about yourself"),
            "issuer_faculty": _("Your faculty"),
        }
        help_texts = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.initial.get("issuer_faculty"):
            self.fields["issuer_faculty"].disabled = True

    # TODO: add save/load of contacts to/from user_profile
