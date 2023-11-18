from __future__ import annotations

from django.apps import apps
from django.core.exceptions import ValidationError
from django.forms import HiddenInput, RadioSelect
from django.utils.translation import gettext_lazy as _

from apps.fiestaforms.forms import BaseModelForm
from apps.plugins.models import Plugin
from apps.plugins.plugin import BasePluginAppConfig
from apps.plugins.utils import all_plugins_mapped_to_label
from apps.sections.services.sections_plugins_validator import SectionPluginsValidator


class ChangePluginStateForm(BaseModelForm):
    instance: Plugin

    class Meta:
        model = Plugin
        fields = ("state",)
        widgets = {
            "state": RadioSelect(),
        }

    def clean(self):
        data: dict = super().clean()

        app: BasePluginAppConfig = all_plugins_mapped_to_label().get(data.get("app_label") or self.instance.app_label)
        if app.auto_enabled and data["state"] != Plugin.State.ENABLED:
            raise ValidationError(_("This plugin is enabled automatically."))

        return data

    def _post_clean(self):
        super()._post_clean()

        try:
            SectionPluginsValidator.for_changed_plugin(
                section=self.instance.section,
                plugin=self.instance,
            ).check_validity()
        except ValidationError as e:
            self.add_error(None, e)


class SetupPluginSettingsForm(ChangePluginStateForm):
    instance: Plugin

    class Meta(ChangePluginStateForm.Meta):
        fields = ChangePluginStateForm.Meta.fields + (
            "app_label",
            "section",
        )
        widgets = {
            "app_label": HiddenInput(),
            "section": HiddenInput(),
        }

    def save(self, commit=True):
        self.instance.configuration = apps.get_model(self.instance.app_config.configuration_model)(
            section=self.instance.section,
            shared=False,
        )
        self.instance.configuration.save()

        return super().save(commit=commit)
