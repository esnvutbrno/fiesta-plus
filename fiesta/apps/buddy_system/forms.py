from __future__ import annotations

from django.core.exceptions import ValidationError
from django.forms import fields_for_model
from django.template.loader import render_to_string
from django.utils.functional import lazy
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User, UserProfile
from apps.buddy_system.models import BuddyRequest, BuddyRequestMatch
from apps.fiestaforms.fields.array import ChoicedArrayField
from apps.fiestaforms.forms import BaseModelForm
from apps.fiestaforms.widgets.models import ActiveLocalMembersFromSectionWidget, UserWidget
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


class BuddyRequestEditorForm(BaseModelForm):
    submit_text = _("Save")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["issuer"].disabled = True

        if self.instance.state != BuddyRequest.State.CREATED:
            # self.fields["matched_by"].disabled = True
            # self.fields["matched_at"].disabled = True
            self.fields["note"].disabled = True
            self.fields["interests"].disabled = True

    class Meta:
        model = BuddyRequest
        fields = (
            "issuer",
            "state",
            "note",
            "interests",
            # "matched_by",
            # "matched_at",
        )
        field_classes = {
            "interests": ChoicedArrayField,
            # "matched_at": DateTimeLocalField,
        }
        widgets = {
            "issuer": UserWidget,
            # "matched_by": ActiveLocalMembersFromSectionWidget,
        }


class QuickBuddyMatchForm(BaseModelForm):
    submit_text = _("Match")
    instance: BuddyRequestMatch

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = BuddyRequestMatch
        fields = ("matcher",)
        widgets = {
            "matcher": ActiveLocalMembersFromSectionWidget,
        }

    def clean_matcher(self):
        matcher: User = self.cleaned_data["matcher"]

        if not matcher.profile_or_none.faculty:
            raise ValidationError(_("This user has not set their faculty. Please ask them to do so or do it yourself."))

        return matcher
