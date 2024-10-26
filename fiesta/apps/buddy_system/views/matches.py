from __future__ import annotations

from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView

from apps.fiestarequests.models.request import BaseRequestProtocol
from apps.plugins.middleware.plugin import HttpRequest
from apps.sections.views.mixins.membership import EnsureLocalUserViewMixin
from apps.utils.breadcrumbs import with_breadcrumb, with_plugin_home_breadcrumb


@with_plugin_home_breadcrumb
@with_breadcrumb(_("My Buddies"))
class MyBuddies(EnsureLocalUserViewMixin, ListView):
    request: HttpRequest

    template_name = "buddy_system/my_buddies.html"

    def get_queryset(self):
        return (
            self.request.user.buddy_system_request_matches.prefetch_related(
                "request__issuer__emailaddress_set",
            )
            .select_related(
                "request__issuer__profile__user",
                "request__issuer__profile__university",
                "request__issuer__profile__faculty",
            )
            .filter(request__state=BaseRequestProtocol.State.MATCHED)
        )
