from __future__ import annotations

from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, TemplateView, UpdateView

from apps.fiestaforms.views.htmx import HtmxFormMixin
from apps.plugins.models import BasePluginConfiguration, Plugin
from apps.plugins.utils import all_plugin_apps
from apps.sections.forms.plugin_configuration import get_plugin_configuration_form
from apps.sections.forms.plugin_state import ChangePluginStateForm, SetupPluginSettingsForm
from apps.sections.views.mixins.membership import EnsureSectionAdminViewMixin
from apps.utils.views import AjaxViewMixin


class SectionPluginsView(
    EnsureSectionAdminViewMixin,
    TemplateView,
):
    template_name = "sections/plugins.html"

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
                        get_plugin_configuration_form(
                            configuration=plugin.configuration,
                            for_section=self.request.in_space_of_section,
                        )(instance=plugin.configuration)
                        if plugin and plugin.configuration
                        else None
                    ),
                    (
                        ChangePluginStateForm(instance=plugin)
                        if plugin
                        else SetupPluginSettingsForm(
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


class PluginDetailMixin(
    EnsureSectionAdminViewMixin,
    HtmxFormMixin,
    AjaxViewMixin,
    SuccessMessageMixin,
):
    model = Plugin
    object: Plugin

    success_url = reverse_lazy("sections:section-plugins")

    ajax_template_name = "sections/parts/plugin_state_form.html"

    extra_context = {
        "PluginState": Plugin.State,
    }

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        data.update(
            {
                "form_url": reverse_lazy("sections:change-plugin-state", kwargs={"pk": self.object.pk}),
            }
        )
        return data


class ChangePluginStateFormView(
    PluginDetailMixin,
    UpdateView,
):
    form_class = ChangePluginStateForm
    success_message = _("Plugin state has been updated.")


class SetupPluginFormView(PluginDetailMixin, CreateView):
    form_class = SetupPluginSettingsForm
    success_message = _("Plugin has been activated.")


class ChangePluginConfigurationFormView(
    EnsureSectionAdminViewMixin,
    HtmxFormMixin,
    AjaxViewMixin,
    SuccessMessageMixin,
    UpdateView,
):
    object: BasePluginConfiguration

    def get_form_class(self):
        return get_plugin_configuration_form(
            configuration=self.object,
            for_section=self.request.in_space_of_section,
        )

    queryset = BasePluginConfiguration.objects.all()

    success_message = _("Plugin configuration has been updated.")
    success_url = reverse_lazy("sections:section-plugins")

    ajax_template_name = "sections/parts/plugin_configuration_form.html"
