from __future__ import annotations

from django.forms import BooleanField, HiddenInput, fields_for_model
from django.template.loader import render_to_string
from django.utils.functional import lazy
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import UserProfile
from apps.buddy_system.models import BuddyRequest
from apps.fiestaforms.fields.array import ChoicedArrayField
from apps.fiestaforms.fields.datetime import DateTimeLocalField
from apps.fiestaforms.forms import BaseModelForm
from apps.fiestaforms.widgets.models import ActiveLocalMembersFromSectionWidget, UserWidget

USER_PROFILE_CONTACT_FIELDS = fields_for_model(
    UserProfile,
    fields=("facebook", "instagram", "telegram", "whatsapp"),
)


class NewBuddyRequestForm(BaseModelForm):
    submit_text = _("Send request for buddy")

    # TODO: group field somehow and add group headings
    facebook, instagram, telegram, whatsapp = USER_PROFILE_CONTACT_FIELDS.values()

    approving_request = BooleanField(required=True, label=_("I really want a buddy"))

    class Meta:
        model = BuddyRequest
        fields = (
            "issuer_note",
            "interests",
            "responsible_section",
            "issuer",
        )
        field_classes = {
            "interests": ChoicedArrayField,
        }
        widgets = {
            "responsible_section": HiddenInput,
            "issuer": HiddenInput,
        }
        labels = {
            "issuer_note": _("Tell us about yourself"),
            "interests": _("What are you into?"),
        }
        help_texts = {
            "issuer_note": lazy(
                lambda: render_to_string("buddy_system/parts/buddy_request_issuer_note_help.html"),
                str,
            )
        }


#     TODO: add save/load of contacts to/from user_profile


class BuddyRequestEditorForm(BaseModelForm):
    submit_text = _("Save")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["issuer"].disabled = True

        if self.instance.state != BuddyRequest.State.CREATED:
            self.fields["matched_by"].disabled = True
            self.fields["matched_at"].disabled = True
            self.fields["issuer_note"].disabled = True
            self.fields["interests"].disabled = True

    class Meta:
        model = BuddyRequest
        fields = (
            "issuer",
            "state",
            "issuer_note",
            "interests",
            "matched_by",
            "matched_at",
        )
        field_classes = {
            "interests": ChoicedArrayField,
            "matched_at": DateTimeLocalField,
        }
        widgets = {
            "issuer": UserWidget,
            "matched_by": ActiveLocalMembersFromSectionWidget,
        }


class QuickBuddyMatchForm(BaseModelForm):
    submit_text = _("Match")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["issuer"].disabled = True

        if self.instance.state != BuddyRequest.State.CREATED:
            self.fields["matched_by"].disabled = True

    class Meta:
        model = BuddyRequest
        fields = (
            "issuer",
            "matched_by",
        )
        widgets = {
            "issuer": UserWidget,
            "matched_by": ActiveLocalMembersFromSectionWidget,
        }
