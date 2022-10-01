from pathlib import Path

from django.views.generic import TemplateView


class DashboardIndexView(TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.apps import apps

        context["blocks"] = {
            app.label: path.as_posix()
            for app, path in (
                (app, (Path(app.path) / "templates" / app.label / "dashboard_block.html"))
                for app in apps.get_app_configs()
            )
            if path.exists()
        }

        return context
