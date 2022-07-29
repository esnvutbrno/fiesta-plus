from django.forms import HiddenInput, BooleanField
from django.template.loader import render_to_string
from django.utils.functional import lazy
from django.utils.translation import gettext_lazy as _

from apps.buddy_system.models import BuddyRequest
from apps.fiestaforms.forms import BaseModelForm
from apps.utils.forms.array import ChoicedArrayField


class NewBuddyRequestForm(BaseModelForm):
    submit_text = _("Send request for buddy")

    approving_request = BooleanField(required=True, label=_("I really want a buddy"))

    class Meta:
        model = BuddyRequest
        fields = (
            "description",
            "interests",
            "responsible_section",
            "issuer",
        )
        field_classes = {"interests": ChoicedArrayField}
        widgets = {
            "responsible_section": HiddenInput,
            "issuer": HiddenInput,
        }
        labels = {
            "description": _("Tell us about yourself"),
            "interests": _("What are you into?"),
        }
        help_texts = {
            "description": lazy(
                lambda: render_to_string(
                    "buddy_system/parts/buddy_request_description_help.html"
                ),
                str,
            )
        }
