from __future__ import annotations

from django.views.generic import TemplateView

from apps.plugins.models import Plugin
from apps.plugins.utils import all_plugins_as_choices
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
                    label,
                    name,
                    by_label(label),
                )
                for label, name in all_plugins_as_choices()
            ],
        )

        return ctx
