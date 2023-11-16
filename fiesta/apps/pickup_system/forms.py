from __future__ import annotations

from django.forms import fields_for_model
from django.template.loader import render_to_string
from django.utils.functional import lazy
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import UserProfile
from apps.fiestarequests.forms.editor import BaseQuickMatchForm, BaseRequestEditorForm
from apps.fiestarequests.forms.request import BaseNewRequestForm
from apps.pickup_system.models import PickupRequest, PickupRequestMatch

USER_PROFILE_CONTACT_FIELDS = fields_for_model(
    UserProfile,
    fields=("facebook", "instagram", "telegram", "whatsapp"),
)


class NewPickupRequestForm(BaseNewRequestForm):
    submit_text = _("Send request for pickup")

    class Meta(BaseNewRequestForm.Meta):
        model = PickupRequest

        fields = BaseNewRequestForm.Meta.fields + ()
        field_classes = BaseNewRequestForm.Meta.field_classes | {}
        labels = BaseNewRequestForm.Meta.labels | {
            "note": _("Tell me details TODO"),
            "interests": _("What are you into?"),
            "approving_request": _("I really want a pickup"),
        }
        help_texts = BaseNewRequestForm.Meta.help_texts | {
            "note": lazy(
                lambda: render_to_string("pickup_system/parts/pickup_request_note_help.html"),
                str,
            )
        }


#     TODO: add save/load of contacts to/from user_profile


class PickupRequestEditorForm(BaseRequestEditorForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta(BaseRequestEditorForm.Meta):
        model = PickupRequest
        fields = BaseRequestEditorForm.Meta.fields + ()
        field_classes = BaseRequestEditorForm.Meta.field_classes | {}
        widgets = BaseRequestEditorForm.Meta.widgets | {}


class QuickPickupMatchForm(BaseQuickMatchForm):
    instance: PickupRequestMatch

    class Meta(BaseQuickMatchForm.Meta):
        model = PickupRequestMatch
