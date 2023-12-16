from __future__ import annotations

from django.forms import BooleanField

from apps.fiestaforms.forms import BaseModelForm


class BaseRequestMatchForm(BaseModelForm):
    approving_request = BooleanField(required=True)

    class Meta:
        # model = BaseRequestMatchProtocol
        fields = ["note"]
        labels = {}
        help_texts = {}
        widgets = {}
