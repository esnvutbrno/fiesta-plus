from __future__ import annotations

from django.views.generic import TemplateView

from apps.sections.views.mixins.membership import EnsurePrivilegedUserViewMixin


class SectionSettingsView(EnsurePrivilegedUserViewMixin, TemplateView):
    template_name = "sections/settings.html"
