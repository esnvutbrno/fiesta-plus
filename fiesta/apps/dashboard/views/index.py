import typing
from pathlib import Path

from django.apps import AppConfig
from django.views.generic import TemplateView

from apps.plugins.models import Plugin
from apps.plugins.plugin import PluginAppConfig
from apps.sections.views.space_mixin import EnsureInSectionSpaceViewMixin


class DashboardIndexView(EnsureInSectionSpaceViewMixin, TemplateView):
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
                for app in self._select_apps_for_dashboard()
            )
            if path.exists()
        }

        return context

    def _select_apps_for_dashboard(self) -> typing.Generator[AppConfig, None, None]:
        from django.apps import apps

        enabled_plugins_apps = self.request.in_space_of_section.plugins.filter(
            state=Plugin.State.ENABLED,
            # TODO: only by state? maybe the R/O or editor is needed
        ).values_list("app_label", flat=True)

        for app in apps.get_app_configs():
            if not isinstance(app, PluginAppConfig):
                # not plugins always shown on dashboard
                yield app

            if app.label in enabled_plugins_apps:
                yield app
