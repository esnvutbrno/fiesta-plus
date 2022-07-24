from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import urlencode


class EnsureInSectionSpaceViewMixin:
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
