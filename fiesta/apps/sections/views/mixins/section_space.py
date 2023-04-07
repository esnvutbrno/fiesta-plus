from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import urlencode

from apps.plugins.middleware.plugin import HttpRequest


class EnsureInSectionSpaceViewMixin:
    """Ensures that we're currently in section space (so on <section>.tld)."""

    request: HttpRequest

    def dispatch(self, request, *args, **kwargs):
        if not self.request.in_space_of_section:
            return redirect(
                "?".join(
                    (
                        reverse("sections:choose-space"),
                        urlencode({REDIRECT_FIELD_NAME: self.request.get_full_path()}),
                    )
                )
            )

        return super().dispatch(request, *args, **kwargs)


class EnsureNotInSectionSpaceViewMixin:
    """Ensures we're not in section space, otherwise redirects to same page but outside section space."""

    request: HttpRequest

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if self.request.in_space_of_section:
            host = (
                request.get_host()
                .removeprefix(request.in_space_of_section.space_slug)
                .removeprefix(".")
            )
            return HttpResponseRedirect(
                f"{request.scheme}://{host}{request.get_full_path()}"
            )

        return super().dispatch(request, *args, **kwargs)
