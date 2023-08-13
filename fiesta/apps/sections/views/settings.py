from __future__ import annotations

from django.forms import modelform_factory
from django.views.generic import TemplateView

from apps.fiestaforms.forms import BaseModelForm
from apps.plugins.models import Plugin
from apps.plugins.utils import all_plugin_apps
from apps.sections.views.mixins.membership import EnsurePrivilegedUserViewMixin


class SectionSettingsView(EnsurePrivilegedUserViewMixin, TemplateView):
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
                )
                for app in all_plugin_apps()
                if (plugin := by_label(app.label)) or True
            ],
        )

        return ctx
