from __future__ import annotations

from django.forms import BooleanField
from django.utils.translation import gettext_lazy as _

from apps.fiestaforms.forms import BaseModelForm


class BaseRequestMatchForm(BaseModelForm):
    approving_request = BooleanField(required=True)

    class Meta:
        # model = BaseRequestMatchProtocol
        fields = ["note"]
        labels = {
            "note": _("Message for your buddy"),
        }
        help_texts = {}
        widgets = {}
