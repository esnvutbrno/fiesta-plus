from django.utils.translation import gettext_lazy as _

from apps.fiestarequests.models import base_request_model_factory


class BuddyRequest(base_request_model_factory("buddy_system")):
    class Meta:
        verbose_name = _("buddy request")
        verbose_name_plural = _("buddy requests")
