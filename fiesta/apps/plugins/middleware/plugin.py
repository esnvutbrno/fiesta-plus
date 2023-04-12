from __future__ import annotations

from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse

from ...sections.middleware.user_membership import HttpRequest as OrigHttpRequest
from ..models import Plugin
from ..utils import target_plugin_app_from_resolver_match


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

        anonymous_allowed = (
            request.resolver_match.url_name in target_app.login_not_required_urls or not target_app.login_required
        )
        if request.user.is_anonymous and not anonymous_allowed:
            # target is plugin view, but request by anonymous user
            # our 403 handler makes the job = redirection to login page
            raise PermissionDenied("Not allowed for anonymous.")

        if not request.membership:
            return

        try:
            plugin: Plugin | None = request.membership.section.plugins.get(
                app_label=target_app.label,
                section_id=request.membership.section_id,
            )
        except Plugin.DoesNotExist as e:
            raise Http404("Plugin is not loaded for selected section.") from e

        request.plugin = plugin

        match request.plugin.state:
            case Plugin.State.ENABLED:
                return
            case Plugin.State.PRIVILEGED_ONLY if request.membership.is_privileged:
                return

        raise PermissionDenied("Plugin is not enabled.")
        # TODO: check, if plugin is enabled, perms and all the stuff


__all__ = ["CurrentPluginMiddleware", "HttpRequest"]
