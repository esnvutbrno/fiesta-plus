from __future__ import annotations

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse

from ..models import Plugin
from ..utils import target_plugin_app_from_resolver_match
from ...sections.middleware.user_membership import HttpRequest as OrigHttpRequest


class HttpRequest(OrigHttpRequest):
    plugin: Plugin | None


class CurrentPluginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: OrigHttpRequest) -> HttpResponse:
        return self.get_response(request)

    def process_view(self, request: HttpRequest, view_func, view_args, view_kwargs):
        request.plugin = None

        target_app = target_plugin_app_from_resolver_match(request.resolver_match)

        if not target_app:
            # target is not a plugin page, so feel free to display on public
            # additional permission should solve each view
            return

        if (
            request.user.is_anonymous
            and request.resolver_match.url_name
            not in target_app.login_not_required_urls
        ):
            # target is plugin view, but request by anonymous user
            # our 403 handler makes the job = redirection to login page
            raise PermissionDenied

        if not request.membership:
            return

        try:
            plugin = request.membership.section.plugins.get(
                app_label=target_app.label,
                section_id=request.membership.section_id,
            )
        except Plugin.DoesNotExist:
            return

        request.plugin = plugin
        # TODO: check, if plugin is enabled, perms and all the stuff


__all__ = ["CurrentPluginMiddleware", "HttpRequest"]
