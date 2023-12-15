from __future__ import annotations

from django.forms import Textarea
from django.template.loader import render_to_string
from django.utils.functional import lazy
from django.utils.translation import gettext_lazy as _

from apps.buddy_system.models import BuddyRequest, BuddyRequestMatch
from apps.fiestaforms.fields.array import ChoicedArrayField
from apps.fiestarequests.forms.editor import BaseQuickMatchForm, BaseRequestEditorForm
from apps.fiestarequests.forms.match import BaseRequestMatchForm
from apps.fiestarequests.forms.request import BaseNewRequestForm


class NewBuddyRequestForm(BaseNewRequestForm):
    submit_text = _("Send request for buddy")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # labels somehow do not work
        self.fields["approving_request"].label = _("Are you sure you want to place a buddy request?")

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


class BuddyRequestMatchForm(BaseRequestMatchForm):
    submit_text = _("Confirm match")

    class Meta(BaseRequestMatchForm.Meta):
        model = BuddyRequestMatch
        labels = BaseRequestMatchForm.Meta.labels | {}
        help_texts = BaseRequestMatchForm.Meta.help_texts | {
            "note": lazy(
                lambda: render_to_string("buddy_system/parts/buddy_request_match_note_help.html"),
                str,
            )
        }
        widgets = BaseRequestMatchForm.Meta.widgets | {
            "note": Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": _(
                        "Hi! I am John and I will be your buddy! The best for communication for me is Telegram, but I"
                        " am basically on all the social platforms. Looking forward to see your and grab a drink"
                        " together!"
                    ),
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # labels somehow do not work
        self.fields["approving_request"].label = _(
            "Are you sure you want to confirm the buddy request, "
            "acknowledging that you will be responsible for being buddy?"
        )
