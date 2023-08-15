from __future__ import annotations

from django.contrib.messages.views import SuccessMessageMixin
from django.forms import modelform_factory
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, UpdateView

from apps.fiestaforms.forms import BaseModelForm
from apps.fiestaforms.views.htmx import HtmxFormMixin
from apps.plugins.models import Plugin
from apps.plugins.utils import all_plugin_apps
from apps.sections.forms.plugin_state import PluginStateSettingsForm
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
                        modelform_factory(
                            plugin.configuration.__class__,
                            form=BaseModelForm,
                            # managed by fiesta/admins
                            exclude=("name", "section", "shared"),
                        )
                        if plugin.configuration
                        else None
                    ),
                    PluginStateSettingsForm(instance=plugin),
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

    # TODO: some of the plugins cannot be disabled (ESN section/dashboard)
