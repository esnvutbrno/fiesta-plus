from django.http import HttpRequest, HttpResponse

from ..models import Plugin


class CurrentPluginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        return self.get_response(request)

    def process_view(self, request: HttpRequest, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated:
            return

        # if not request.membership:
        #     # TODO: not active membership, redirect or?
        #     return

        # TODO: resolver.app_name is full-dotted path
        # Plugin.app_label is just ending section
        # is there a cleaner way?
        target_app = request.resolver_match.app_name.split(".")[-1]

        try:
            # TODO: decide, which section -> which plugin
            request.plugin = Plugin.objects.get(app_label=target_app)
        except Plugin.DoesNotExist:
            request.plugin = None
            return

        # TODO: check, if plugin is enabled, perms and all the stuff


__all__ = ["CurrentPluginMiddleware"]
