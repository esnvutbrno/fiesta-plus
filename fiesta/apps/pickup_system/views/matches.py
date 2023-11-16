from __future__ import annotations

from django.views.generic import ListView

from apps.plugins.middleware.plugin import HttpRequest
from apps.sections.views.mixins.membership import EnsureLocalUserViewMixin


class MyPickups(EnsureLocalUserViewMixin, ListView):
    request: HttpRequest

    template_name = "pickup_system/my_pickups.html"

    def get_queryset(self):
        return self.request.user.pickup_system_request_matches.prefetch_related(
            "request__issuer__profile"
        ).select_related("request", "matcher")
