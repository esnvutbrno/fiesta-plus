from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django.views.defaults import permission_denied


def handler_403(request: HttpRequest, exception: Exception):
    if request.user.is_anonymous:
        messages.warning(request, _("To view this page please authenticate yourself."))
        return redirect_to_login(request.get_full_path())

    return permission_denied(request, exception)
