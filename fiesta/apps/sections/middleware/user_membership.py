from __future__ import annotations

from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import ResolverMatch, reverse
from django.utils.translation import gettext_lazy as _

from ..models import SectionMembership
from ...plugins.plugin import PluginAppConfig
from ...plugins.utils import target_plugin_app_from_resolver_match
from ...utils.request import HttpRequest as OrigHttpRequest


class HttpRequest(OrigHttpRequest):
    membership: SectionMembership | None


class UserMembershipMiddleware:
    MEMBERSHIP_URL_NAME = "accounts:membership"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: OrigHttpRequest) -> HttpResponse:
        request.membership = None

        if request.user.is_anonymous:
            return self.get_response(request)

        # TODO: Detect, in which membership is user logged:
        #  probably the default one, with possibility to switch
        #  with sesstion flag
        request.membership = (
            request.user.memberships.select_related(
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
        target_app = target_plugin_app_from_resolver_match(request.resolver_match)

        if not target_app:
            # target apps are not plugin, so probably public
            # additional checks needs to be in views itself
            return

        if cls.should_ignore(target_app, request.resolver_match):
            # on membership page, so fine -> we don't want to loop
            # or urls is not requiring logged user (=membership)
            return

        if (
            not request.membership
            and request.resolver_match.url_name
            not in target_app.membership_not_required_urls
        ):
            # target is plugin view, but user does not have any membership,
            # and we're not on memberships page
            # (and url is not whitelisted)
            messages.warning(
                request, _("You don't have any active membership to view this page.")
            )
            return HttpResponseRedirect(reverse(cls.MEMBERSHIP_URL_NAME))

    @classmethod
    def should_ignore(cls, target_app: PluginAppConfig, resolver_match: ResolverMatch):
        """Checks if specific request for specific plugin should be excluded from existing membership check."""
        on_membership_page = resolver_match.view_name.startswith(
            cls.MEMBERSHIP_URL_NAME
        )

        anonymnous_allowed = (
            resolver_match.url_name in target_app.login_not_required_urls
        )

        return on_membership_page or anonymnous_allowed


__all__ = ["UserMembershipMiddleware", "HttpRequest"]
