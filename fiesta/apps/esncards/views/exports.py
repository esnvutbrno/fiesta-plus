from __future__ import annotations

from django.views.generic import TemplateView


class NewExportView(TemplateView):
    template_name = "esncards/new_export.html"
