from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest as DjHttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import ResolverMatch, reverse
from django.utils.translation import gettext_lazy as _

from ..models import SectionMembership
from ...accounts.models import User
from ...plugins.utils import target_plugin_app_from_resolver_match


class HttpRequest(DjHttpRequest):
    membership: SectionMembership | None


class UserMembershipMiddleware:
    MEMBERSHIP_URL_NAME = "accounts:membership"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: DjHttpRequest) -> HttpResponse:
        user: User | AnonymousUser = request.user

        request.membership = None

        if user.is_anonymous:
            return self.get_response(request)

        # TODO: Detect, in which membership is user logged:
        #  probably the default one, with possibility to switch
        #  with sesstion flag
        request.membership = (
            user.memberships.select_related(
                # to remove another query for relating section
                "section"
            )
            .filter(
                state=SectionMembership.State.ACTIVE,
            )
            .first()
        )

        return self.get_response(request)

    @classmethod
    def process_view(cls, request: HttpRequest, view_func, view_args, view_kwargs):
        target_plugin = target_plugin_app_from_resolver_match(request.resolver_match)

        if not target_plugin:
            # target apps are not plugin, so probably public
            # additional checks needs to be in views itself
            return

        if cls.should_ignore(request.resolver_match):
            # on membership page, so fine -> we don't want to loop
            return

        if not request.membership:
            # target is plugin view, but user does not have any membership,
            # and we're not on memberships page
            messages.warning(
                request, _("You don't have any active membership to view this page.")
            )
            return HttpResponseRedirect(reverse(cls.MEMBERSHIP_URL_NAME))

    @classmethod
    def should_ignore(cls, resolver_match: ResolverMatch):
        return resolver_match.view_name.startswith(cls.MEMBERSHIP_URL_NAME)


__all__ = ["UserMembershipMiddleware", "HttpRequest"]
