from __future__ import annotations

from django.forms import Textarea, fields_for_model
from django.template.loader import render_to_string
from django.utils.functional import lazy
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import UserProfile
from apps.fiestaforms.fields.datetime import DateTimeLocalField
from apps.fiestaforms.forms import WebpackMediaFormMixin
from apps.fiestarequests.forms.editor import BaseQuickMatchForm, BaseRequestEditorForm
from apps.fiestarequests.forms.match import BaseRequestMatchForm
from apps.fiestarequests.forms.request import BaseNewRequestForm
from apps.pickup_system.models import PickupRequest, PickupRequestMatch

USER_PROFILE_CONTACT_FIELDS = fields_for_model(
    UserProfile,
    fields=("facebook", "instagram", "telegram", "whatsapp"),
)


class NewPickupRequestForm(WebpackMediaFormMixin, BaseNewRequestForm):
    _webpack_bundle = "jquery"
    submit_text = _("Send request for pickup")

    class Meta(BaseNewRequestForm.Meta):
        model = PickupRequest

        fields = (
            (
                "time",
                "place",
                "location",
            )
            + BaseNewRequestForm.Meta.fields
            + ()
        )
        field_classes = BaseNewRequestForm.Meta.field_classes | {"time": DateTimeLocalField}
        widgets = BaseNewRequestForm.Meta.widgets | {}
        labels = BaseNewRequestForm.Meta.labels | {
            "note": _("Tell me details TODO"),
            "interests": _("What are you into?"),
            "approving_request": _("I really want a pickup"),
            "place": _("Where do you want to be picked up?"),
            "location": _("Place marker as accurately as possible"),
        }
        help_texts = BaseNewRequestForm.Meta.help_texts | {
            "note": lazy(
                lambda: render_to_string("pickup_system/parts/pickup_request_note_help.html"),
                str,
            )
        }


#     TODO: add save/load of contacts to/from user_profile


class PickupRequestEditorForm(WebpackMediaFormMixin, BaseRequestEditorForm):
    _webpack_bundle = "jquery"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta(BaseRequestEditorForm.Meta):
        model = PickupRequest
        fields = BaseRequestEditorForm.Meta.fields + (
            "time",
            "place",
            "location",
        )
        field_classes = BaseRequestEditorForm.Meta.field_classes | {}
        widgets = BaseRequestEditorForm.Meta.widgets | {}


class QuickPickupMatchForm(BaseQuickMatchForm):
    instance: PickupRequestMatch

    class Meta(BaseQuickMatchForm.Meta):
        model = PickupRequestMatch


class PickupRequestMatchForm(BaseRequestMatchForm):
    submit_text = _("Confirm pickup")

    class Meta(BaseRequestMatchForm.Meta):
        model = PickupRequestMatch
        labels = BaseRequestMatchForm.Meta.labels | {}
        help_texts = BaseRequestMatchForm.Meta.help_texts | {
            "note": lazy(
                lambda: render_to_string("pickup_system/parts/pickup_request_match_note_help.html"),
                str,
            )
        }
        widgets = BaseRequestMatchForm.Meta.widgets | {
            "note": Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": _(
                        "Hi! I am John and I will pick you up! "
                        "The best for communication for me is Telegram, but I am basically on all the social platforms. "
                        "Looking forward to see your and grab a drink together!"
                    ),
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # labels somehow do not work
        self.fields["approving_request"].label = _(
            "Are you sure you want to confirm the pickup request, "
            "acknowledging that you will be responsible for pickup?"
        )
