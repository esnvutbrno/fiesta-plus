from __future__ import annotations

from django.core.exceptions import ValidationError
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

        fields = BaseNewRequestForm.Meta.fields + ("interests", "same_gender_only")
        field_classes = BaseNewRequestForm.Meta.field_classes | {
            "interests": ChoicedArrayField,
        }
        labels = BaseNewRequestForm.Meta.labels | {
            "note": _("Tell us about yourself"),
            "interests": _("What are you into?"),
            "approving_requests": _("I really want a buddy"),
            "same_gender_only": _("Only match me with a buddy of the same gender"),
        }
        help_texts = BaseNewRequestForm.Meta.help_texts | {
            "note": lazy(
                lambda: render_to_string("buddy_system/parts/buddy_request_note_help.html"),
                str,
            ),
            "same_gender_only": _(
                "Only available if your profile gender is set to male or female. If selected, you will "
                "only be matched with a buddy of the same gender as you."
            ),
        }


class BuddyRequestEditorForm(BaseRequestEditorForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.state != BuddyRequest.State.CREATED:
            self.fields["interests"].disabled = True

        # surface the same-gender constraint to editors as read-only info; hide it when irrelevant
        if self.instance.same_gender_only:
            field = self.fields["same_gender_only"]
            field.disabled = True
            field.label = _("Same-gender buddy only")
            field.help_text = _(
                "This student asked to be matched only with a buddy of the same gender (%(gender)s)."
            ) % {"gender": self.instance.get_issuer_gender_display()}
        else:
            del self.fields["same_gender_only"]

    class Meta(BaseRequestEditorForm.Meta):
        model = BuddyRequest
        fields = BaseRequestEditorForm.Meta.fields + ("interests", "same_gender_only")
        field_classes = BaseRequestEditorForm.Meta.field_classes | {
            "interests": ChoicedArrayField,
        }
        widgets = BaseRequestEditorForm.Meta.widgets | {}


class QuickBuddyMatchForm(BaseQuickMatchForm):
    # NOTE: at runtime `self.instance` is actually a BuddyRequest, not a BuddyRequestMatch --
    # QuickBuddyMatchView is an UpdateView with model=BuddyRequest, so get_object() (a BuddyRequest)
    # is passed in as the form instance; this annotation only describes the form's Meta.model
    instance: BuddyRequestMatch

    class Meta(BaseQuickMatchForm.Meta):
        model = BuddyRequestMatch

    def __init__(self, *args, same_gender_matching_enabled: bool = False, **kwargs):
        self._same_gender_matching_enabled = same_gender_matching_enabled
        super().__init__(*args, **kwargs)

    def clean_matcher(self):
        matcher = super().clean_matcher()

        if (
            self._same_gender_matching_enabled
            and self.instance.same_gender_only
            and matcher.profile_or_none.gender != self.instance.issuer_gender
        ):
            raise ValidationError(_("This request can only be matched with a buddy of the same gender."))

        return matcher


class BuddyRequestMatchForm(BaseRequestMatchForm):
    submit_text = _("Confirm match")

    class Meta(BaseRequestMatchForm.Meta):
        model = BuddyRequestMatch
        labels = BaseRequestMatchForm.Meta.labels | {
            "note": _("Message for your upcoming buddy"),
        }
        help_texts = BaseRequestMatchForm.Meta.help_texts | {}
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
