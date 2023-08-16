from __future__ import annotations

from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, TemplateView, UpdateView

from apps.fiestaforms.views.htmx import HtmxFormMixin
from apps.plugins.models import BasePluginConfiguration, Plugin
from apps.plugins.utils import all_plugin_apps
from apps.sections.forms.plugin_configuration import get_plugin_configuration_form
from apps.sections.forms.plugin_state import CreatePluginSettingsForm, PluginStateSettingsForm
from apps.sections.views.mixins.membership import EnsureSectionAdminViewMixin
from apps.utils.views import AjaxViewMixin


class SectionSettingsView(
    EnsureSectionAdminViewMixin,
    TemplateView,
):
    template_name = "sections/settings.html"

    def get_context_data(self, **kwargs):
        def by_label(label: str) -> Plugin | None:
            return self.request.in_space_of_section.plugins.filter(app_label=label).first()

        ctx = super().get_context_data(**kwargs)
        ctx.update(
            plugins=[
                (
                    app,
                    plugin,
                    (
                        get_plugin_configuration_form(plugin.configuration)(instance=plugin.configuration)
                        if plugin and plugin.configuration
                        else None
                    ),
                    (
                        PluginStateSettingsForm(instance=plugin)
                        if plugin
                        else CreatePluginSettingsForm(
                            initial={
                                "app_label": app.label,
                                "section": self.request.in_space_of_section,
                            }
                        )
                    ),
                )
                for app in all_plugin_apps()
                if (plugin := by_label(app.label)) or True
            ],
            PluginState=Plugin.State,
        )

        return ctx


class ChangePluginStateFormView(
    EnsureSectionAdminViewMixin,
    HtmxFormMixin,
    AjaxViewMixin,
    SuccessMessageMixin,
    UpdateView,
):
    form_class = PluginStateSettingsForm
    model = Plugin

    success_message = _("Plugin state has been updated.")
    success_url = reverse_lazy("sections:section-settings")

    ajax_template_name = "sections/parts/settings_plugin_state_form.html"

    extra_context = {
        "PluginState": Plugin.State,
    }


class CreatePluginFormView(
    EnsureSectionAdminViewMixin,
    HtmxFormMixin,
    AjaxViewMixin,
    SuccessMessageMixin,
    CreateView,
):
    form_class = CreatePluginSettingsForm
    model = Plugin

    success_message = _("Plugin has been activated.")
    success_url = reverse_lazy("sections:section-settings")

    ajax_template_name = "sections/parts/settings_plugin_state_form.html"

    extra_context = {
        "PluginState": Plugin.State,
        "form_url": reverse_lazy("sections:create-plugin"),
    }


class ChangePluginConfigurationFormView(
    EnsureSectionAdminViewMixin,
    HtmxFormMixin,
    AjaxViewMixin,
    SuccessMessageMixin,
    UpdateView,
):
    object: BasePluginConfiguration

    def get_form_class(self):
        return get_plugin_configuration_form(self.object)

    queryset = BasePluginConfiguration.objects.all()

    success_message = _("Plugin configuration has been updated.")
    success_url = reverse_lazy("sections:section-settings")

    ajax_template_name = "sections/parts/settings_plugin_configuration_form.html"
