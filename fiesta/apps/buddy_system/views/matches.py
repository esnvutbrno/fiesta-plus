from __future__ import annotations

from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView
from django.db.models import Prefetch
from apps.accounts.models import UserProfile
from apps.accounts.models.user import User

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
        user_profile_prefetch = Prefetch(
            'request__issuer__profile',
            queryset=UserProfile.objects.select_related('user', 'university', 'faculty')
        )
        return (
            self.request.user.buddy_system_request_matches.select_related('request__issuer').prefetch_related(user_profile_prefetch)
            .filter(
                request__state=BaseRequestProtocol.State.MATCHED
            )
        )