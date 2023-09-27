from typing import Any
from django.db import models
from django.views.generic import CreateView, ListView
from apps.sections.views.mixins.membership import EnsurePrivilegedUserViewMixin
from allauth.account.utils import get_next_redirect_url
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.auth import REDIRECT_FIELD_NAME
from ..models.event import Event
from apps.utils.views import AjaxViewMixin
from apps.fiestaforms.views.htmx import HtmxFormMixin
from django.contrib.messages.views import SuccessMessageMixin
from apps.plugins.middleware.plugin import HttpRequest
from apps.events.forms.event import AddEventForm
from apps.utils.breadcrumbs import with_breadcrumb, with_object_breadcrumb
from apps.sections.models.section import Section

class EventView(ListView):
    template_name='events/index.html'
    model = Event
    
    def get_queryset(self):
        return super().get_queryset()
    
class AddEventView(
    CreateView, 
    HtmxFormMixin,
    AjaxViewMixin,
    SuccessMessageMixin
    ):
    
    request: HttpRequest
    object: Event

    template_name='events/add_event.html'
    ajax_template_name = 'events/parts/add_event_form.html'

    form_class = AddEventForm
    
    success_message = _("Event added")

    def get_initial(self):
        print(self.request.in_space_of_section.id)
        return dict(
            section = self.request.in_space_of_section,
        )

    def get_success_url(self):
        return reverse("events:index")
