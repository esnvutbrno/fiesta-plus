from __future__ import annotations

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from apps.fiestarequests.views.request import BaseNewRequestView
from apps.pickup_system.forms import NewPickupRequestForm
from apps.pickup_system.models import PickupSystemConfiguration
from apps.plugins.views import PluginConfigurationViewMixin
from apps.utils.breadcrumbs import with_breadcrumb, with_plugin_home_breadcrumb


@with_plugin_home_breadcrumb
@with_breadcrumb(_("New pickup request"))
class NewPickupRequestView(
    PluginConfigurationViewMixin[PickupSystemConfiguration],
    BaseNewRequestView,
):
    form_class = NewPickupRequestForm
    success_message = _("Your pickup request has been successfully created!")

    success_url = reverse_lazy("pickup_system:index")

    def get_initial(self):
        initial = super().get_initial()
        initial.update(
            location=self.configuration.default_pickup_location,
        )
        return initial
