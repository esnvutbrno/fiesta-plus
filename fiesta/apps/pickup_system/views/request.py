from __future__ import annotations

from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from apps.fiestarequests.views.request import BaseNewRequestView
from apps.pickup_system.forms import NewPickupRequestForm
from apps.pickup_system.models import PickupSystemConfiguration
from apps.plugins.views import PluginConfigurationViewMixin
from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin
from apps.utils.breadcrumbs import with_breadcrumb, with_plugin_home_breadcrumb


class PickupSystemEntrance(EnsureInSectionSpaceViewMixin, PluginConfigurationViewMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        if self.request.membership.is_international:
            return HttpResponseRedirect(reverse("pickup_system:new-request"))

        c: PickupSystemConfiguration = self.configuration
        if c.matching_policy_instance.can_member_match:
            return HttpResponseRedirect(reverse("pickup_system:matching-requests"))

        return HttpResponseRedirect(reverse("pickup_system:index"))


@with_plugin_home_breadcrumb
@with_breadcrumb(_("New pickup request"))
class NewPickupRequestView(BaseNewRequestView):
    form_class = NewPickupRequestForm
    success_message = _("Your pickup request has been successfully created!")

    success_url = reverse_lazy("pickup_system:index")
