from __future__ import annotations

import typing
from pathlib import Path

from django.apps import AppConfig
from django.views.generic import TemplateView

from apps.plugins.plugin import BasePluginAppConfig
from apps.plugins.views.mixins import CheckEnabledPluginsViewMixin
from apps.sections.models import SectionMembership
from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin


class DashboardIndexView(EnsureInSectionSpaceViewMixin, CheckEnabledPluginsViewMixin, TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["blocks"] = {
            app.label: path.as_posix()
            for app, path in (
                (
                    app,
                    (Path(app.path) / "templates" / app.label / "dashboard_block.html"),
                )
                for app in self._select_apps_for_dashboard(self.request.membership)
            )
            if path.exists()
        }

        return context

    def _select_apps_for_dashboard(self, membership: SectionMembership) -> typing.Generator[AppConfig, None, None]:
        from django.apps import apps

        enabled_plugins_apps = self._get_enabled_plugin_app_labels(
            in_space_of_section=self.request.in_space_of_section,
            membership=membership,
        )

        for app in apps.get_app_configs():
            if not isinstance(app, BasePluginAppConfig):
                # not plugins always shown on dashboard
                yield app

            if app.label in enabled_plugins_apps:
                yield app
