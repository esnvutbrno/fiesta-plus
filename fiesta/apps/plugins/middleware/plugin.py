from __future__ import annotations

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse

from ...sections.middleware.user_membership import HttpRequest as OrigHttpRequest
from ..models import Plugin


class HttpRequest(OrigHttpRequest):
    plugin: Plugin | None


class CurrentPluginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: OrigHttpRequest) -> HttpResponse:
        if not hasattr(request, "membership"):
            raise ImproperlyConfigured(
                "Missing request.membership, probably the "
                '"apps.sections.middleware.user_membership.UserMembershipMiddleware" is not included'
            )
        return self.get_response(request)

    def process_view(self, request: HttpRequest, view_func, view_args, view_kwargs):
        # if not request.user.is_authenticated:
        #     return

        if not request.membership:
            # TODO: not active membership, redirect or?
            return

        if not request.resolver_match.app_name:
            # no app --> cannot resolve plugin
            return

        # TODO: resolver.app_name is full-dotted path
        # Plugin.app_label is just ending section
        # is there a cleaner way?
        target_app = request.resolver_match.app_name.split(".")[-1]

        try:
            request.plugin = Plugin.objects.get(
                app_label=target_app,
                section_id=request.membership.section_id,
            )
        except Plugin.DoesNotExist:
            request.plugin = None
            return
        # TODO: check, if plugin is enabled, perms and all the stuff


__all__ = ["CurrentPluginMiddleware", "HttpRequest"]
