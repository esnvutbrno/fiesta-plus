from django.http import Http404

from apps.plugins.middleware.plugin import HttpRequest


class EnsureLocalMembershipViewMixin:
    request: HttpRequest

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not self.request.membership.is_local:
            # TODO: maybe specific error page? idk
            raise Http404

        return super().dispatch(request, *args, **kwargs)


class EnsureInternationalMembershipViewMixin:
    request: HttpRequest

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not self.request.membership.is_international:
            # TODO: maybe specific error page? idk
            raise Http404

        return super().dispatch(request, *args, **kwargs)
