from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.db.models.query import QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import ResolverMatch, reverse
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _

from ..models import SectionMembership
from ...plugins.plugin import PluginAppConfig
from ...plugins.utils import target_plugin_app_from_resolver_match
from ...sections.middleware.section_space import HttpRequest as BaseHttpRequest


class HttpRequest(BaseHttpRequest):
    # single one active membership or None
    membership: SectionMembership | None
    # all users memberships (including inactive)
    all_memberships: QuerySet[SectionMembership] | None


class UserMembershipMiddleware:
    """
    Well. It works. Would be better to include unit tests, or at least flow diagram.
    :-(
    """

    MEMBERSHIP_URL_NAME = "accounts:membership"
    MEMBERSHIP_NEW_URL_NAME = "accounts:membership-new"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: BaseHttpRequest) -> HttpResponse:
        request.membership = request.all_memberships = None
        return self.get_response(request)

    @classmethod
    def process_view(cls, request: HttpRequest, view_func, view_args, view_kwargs):
        request.all_memberships = None

        if request.user.is_authenticated:
            return

        # to remove another query for relating section
        request.all_memberships = request.user.memberships.select_related("section")

        target_app = target_plugin_app_from_resolver_match(request.resolver_match)

        membership = (
            # (section+user) are unique together, so .first() to get only one or None
            request.all_memberships.filter(
                section=request.in_space_of_section,
            ).first()
        )
        # user in section space with active membership?
        if membership and membership.state == SectionMembership.State.ACTIVE:
            # everything alright! :clap-clap
            request.membership = membership
            return

        if not target_app:
            # target apps are not plugin, so probably public
            # additional checks needs to be in views itself
            return

        if request.in_space_of_section and not membership:
            # hohoo, whatcha doing here, go away
            host = (
                request.get_host()
                .removeprefix(request.in_space_of_section.space_slug)
                .removeprefix(".")
            )
            messages.warning(
                request, _("You have no permission to access this section space.")
            )
            return HttpResponseRedirect(
                f"{request.scheme}://{host}{reverse(cls.MEMBERSHIP_URL_NAME)}"
            )

        if not cls.should_ignore_403(target_app, request.resolver_match):
            # target is plugin view, but user does not have any membership,
            # and we're not on membership page

            # user in section space with inactive membership yet?
            if membership and membership.state == SectionMembership.State.INACTIVE:
                messages.warning(request, _("Your membership is not active yet."))
            elif membership and membership.state == SectionMembership.State.SUSPENDED:
                messages.warning(request, _("Your membership has been suspended."))
            else:
                messages.warning(
                    request, _("You don't have no active membership to view this page.")
                )

            if not membership and request.in_space_of_section:
                # in specific section space, but no membership --> provide form
                messages.warning(
                    request,
                    _("For this section you have no membership, you can ask for one."),
                )
                return HttpResponseRedirect(
                    "?".join(
                        (
                            reverse(
                                cls.MEMBERSHIP_NEW_URL_NAME,
                                args=(request.in_space_of_section,),
                            ),
                            urlencode({REDIRECT_FIELD_NAME: request.get_full_path()}),
                        )
                    )
                )

            # no section space, so display all memberships

            return HttpResponseRedirect(reverse(cls.MEMBERSHIP_URL_NAME))

    @classmethod
    def should_ignore_403(
        cls, target_app: PluginAppConfig, resolver_match: ResolverMatch
    ):
        """Checks if specific request for specific plugin should be excluded from existing membership check."""
        anonymnous_allowed = (
            resolver_match.url_name in target_app.login_not_required_urls
        )

        return (
            cls.is_membership_view(resolver_match=resolver_match) or anonymnous_allowed
        )

    @classmethod
    def is_membership_view(cls, resolver_match: ResolverMatch):
        return resolver_match.view_name.startswith(cls.MEMBERSHIP_URL_NAME)


__all__ = ["UserMembershipMiddleware", "HttpRequest"]
