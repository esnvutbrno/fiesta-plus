from __future__ import annotations

from django.views.generic import ListView

from apps.plugins.middleware.plugin import HttpRequest


class EsncardIndexView(ListView):
    template_name = "esncards/index.html"
    request: HttpRequest

    def get_queryset(self):
        return (
            self.request.user.esncard_applications.filter(
                section=self.request.in_space_of_section,
            )
            if self.request.in_space_of_section
            else self.request.user.esncard_applications.all()
        )
