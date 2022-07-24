from django.forms import HiddenInput
from django.utils.translation import gettext_lazy as _

from apps.buddy_system.models import BuddyRequest
from apps.fiestaforms.forms import BaseModelForm


class NewRequestForm(BaseModelForm):
    submit_text = _("Request for buddy")

    class Meta:
        model = BuddyRequest
        fields = (
            # TODO: add notes, interests, etc
        )
        widgets = {
            "responsible_section": HiddenInput,
            "issuer": HiddenInput,
        }
