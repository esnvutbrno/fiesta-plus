from __future__ import annotations

from django.core.exceptions import ValidationError
from django.forms import RadioSelect
from django.utils.translation import gettext_lazy as _

from apps.fiestaforms.forms import BaseModelForm
from apps.plugins.models import Plugin


class PluginStateSettingsForm(BaseModelForm):
    instance: Plugin

    class Meta:
        model = Plugin
        fields = ("state",)
        widgets = {
            "state": RadioSelect(),
        }

    def clean_state(self):
        if self.instance.app_config.auto_enabled and self.cleaned_data["state"] != Plugin.State.ENABLED:
            raise ValidationError(_("This plugin is enabled automatically."))

        return self.cleaned_data["state"]
