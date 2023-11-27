from __future__ import annotations

from django_htmx.http import HttpResponseClientRedirect


class HtmxFormViewMixin:
    def form_valid(self, form):
        """If the form is valid, redirect to the supplied URL."""
        super().form_valid(form)
        return HttpResponseClientRedirect(self.get_success_url())
