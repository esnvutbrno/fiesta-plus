from __future__ import annotations

from django.core.exceptions import ValidationError
from django.forms import BooleanField, HiddenInput, fields_for_model
from django.template.loader import render_to_string
from django.utils.functional import lazy
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User, UserProfile
from apps.fiestaforms.forms import BaseModelForm
from apps.fiestaforms.widgets.models import ActiveLocalMembersFromSectionWidget, FacultyWidget, UserWidget
from apps.pickup_system.models import PickupRequest, PickupRequestMatch

USER_PROFILE_CONTACT_FIELDS = fields_for_model(
    UserProfile,
    fields=("facebook", "instagram", "telegram", "whatsapp"),
)


class NewPickupRequestForm(BaseModelForm):
    submit_text = _("Send request for pickup")

    # TODO: group field somehow and add group headings
    facebook, instagram, telegram, whatsapp = USER_PROFILE_CONTACT_FIELDS.values()

    approving_request = BooleanField(required=True, label=_("I really want a pickup"))

    class Meta:
        model = PickupRequest
        fields = (
            "note",
            # "interests",
            "issuer",
            "issuer_faculty",
        )
        field_classes = {
            # "interests": ChoicedArrayField,
        }
        widgets = {
            "issuer": HiddenInput,
            "issuer_faculty": FacultyWidget,
        }
        labels = {
            "note": _("Tell us about yourself"),
            # "interests": _("What are you into?"),
            "issuer_faculty": _("Your faculty"),
        }
        help_texts = {
            "note": lazy(
                lambda: render_to_string("pickup_system/parts/pickup_request_note_help.html"),
                str,
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.initial.get("issuer_faculty"):
            self.fields["issuer_faculty"].disabled = True


#     TODO: add save/load of contacts to/from user_profile


class PickupRequestEditorForm(BaseModelForm):
    submit_text = _("Save")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["issuer"].disabled = True

        if self.instance.state != PickupRequest.State.CREATED:
            # self.fields["matched_by"].disabled = True
            # self.fields["matched_at"].disabled = True
            self.fields["note"].disabled = True
            # self.fields["interests"].disabled = True

    class Meta:
        model = PickupRequest
        fields = (
            "issuer",
            "state",
            "note",
            # "interests",
            # "matched_by",
            # "matched_at",
        )
        field_classes = {
            # "interests": ChoicedArrayField,
            # "matched_at": DateTimeLocalField,
        }
        widgets = {
            "issuer": UserWidget,
            # "matched_by": ActiveLocalMembersFromSectionWidget,
        }


class QuickPickupMatchForm(BaseModelForm):
    submit_text = _("Match")
    instance: PickupRequestMatch

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = PickupRequestMatch
        fields = ("matcher",)
        widgets = {
            "matcher": ActiveLocalMembersFromSectionWidget,
        }

    def clean_matcher(self):
        matcher: User = self.cleaned_data["matcher"]

        if not matcher.profile_or_none.faculty:
            raise ValidationError(_("This user has not set their faculty. Please ask them to do so or do it yourself."))

        return matcher
