from __future__ import annotations

from django.forms import RadioSelect

from apps.fiestaforms.forms import BaseModelForm
from apps.plugins.models import Plugin


class PluginStateForm(BaseModelForm):
    class Meta:
        model = Plugin
        fields = ("state",)
        widgets = {
            "state": RadioSelect(),
        }
