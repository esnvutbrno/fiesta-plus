from __future__ import annotations

from django.forms import fields_for_model
from django.template.loader import render_to_string
from django.utils.functional import lazy
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import UserProfile
from apps.buddy_system.models import BuddyRequest, BuddyRequestMatch
from apps.fiestaforms.fields.array import ChoicedArrayField
from apps.fiestarequests.forms.editor import BaseQuickMatchForm, BaseRequestEditorForm
from apps.fiestarequests.forms.request import BaseNewRequestForm

USER_PROFILE_CONTACT_FIELDS = fields_for_model(
    UserProfile,
    fields=("facebook", "instagram", "telegram", "whatsapp"),
)


class NewBuddyRequestForm(BaseNewRequestForm):
    submit_text = _("Send request for buddy")

    class Meta(BaseNewRequestForm.Meta):
        model = BuddyRequest

        fields = BaseNewRequestForm.Meta.fields + ("interests",)
        field_classes = BaseNewRequestForm.Meta.field_classes | {
            "interests": ChoicedArrayField,
        }
        labels = BaseNewRequestForm.Meta.labels | {
            "note": _("Tell us about yourself"),
            "interests": _("What are you into?"),
            "approving_requests": _("I really want a buddy"),
        }
        help_texts = BaseNewRequestForm.Meta.help_texts | {
            "note": lazy(
                lambda: render_to_string("buddy_system/parts/buddy_request_note_help.html"),
                str,
            )
        }


class BuddyRequestEditorForm(BaseRequestEditorForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.state != BuddyRequest.State.CREATED:
            self.fields["interests"].disabled = True

    class Meta(BaseRequestEditorForm.Meta):
        model = BuddyRequest
        fields = BaseRequestEditorForm.Meta.fields + ("interests",)
        field_classes = BaseRequestEditorForm.Meta.field_classes | {
            "interests": ChoicedArrayField,
        }
        widgets = BaseRequestEditorForm.Meta.widgets | {}


class QuickBuddyMatchForm(BaseQuickMatchForm):
    instance: BuddyRequestMatch

    class Meta(BaseQuickMatchForm.Meta):
        model = BuddyRequestMatch
