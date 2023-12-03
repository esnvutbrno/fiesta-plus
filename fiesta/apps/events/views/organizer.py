import json
from typing import Any
from uuid import UUID
from django import http
from django.forms.models import BaseModelForm

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404

import django_filters
from django.contrib.postgres.search import SearchVector
from django.forms import TextInput
from django.views.generic import CreateView, DeleteView, UpdateView, ListView, View
import django_tables2 as tables

from django.utils.translation import gettext_lazy as _
from django.urls import reverse, reverse_lazy
from django_filters import CharFilter, ChoiceFilter
from django_tables2 import Column
from django.db import models

from ..models import Participant
from ..models.event import Event, EventState
from apps.utils.views import AjaxViewMixin
from apps.fiestaforms.views.htmx import HtmxFormViewMixin
from django.contrib.messages.views import SuccessMessageMixin
from apps.plugins.middleware.plugin import HttpRequest
from apps.events.forms.event import AddEventForm, UpdateEventForm

from ..models.participant import ParticipantState
from ..models.organizer import Organizer, OrganizerRole
from ...fiestatables.columns import ImageColumn, NaturalDatetimeColumn, LabeledChoicesColumn
from ...fiestatables.filters import BaseFilterSet, ProperDateFromToRangeFilter
from ...fiestatables.views.tables import FiestaTableView
from ...sections.views.mixins.membership import EnsurePrivilegedUserViewMixin
from ...utils.breadcrumbs import with_breadcrumb
from allauth.account.utils import get_next_redirect_url
from django.contrib.auth import REDIRECT_FIELD_NAME
from apps.events.forms.organizer import OrganizerForm
from django.utils.html import format_html
from django.http import JsonResponse
from django.db import transaction


class UpdateOrganizerRole(AjaxViewMixin, SuccessMessageMixin, HtmxFormViewMixin ,EnsurePrivilegedUserViewMixin, View):
    model = Organizer
    
    def dispatch(self, request, *args, **kwargs):
        self.event = get_object_or_404(Event, pk=self.kwargs.get("pk"))
        self.organizer = get_object_or_404(Organizer, pk=self.kwargs.get("pko"))
        return super().dispatch(request, *args, **kwargs)
    

    def post(self, request, pk, pko):
        if request.POST.get('role') == "event_leader":
            self.organizer.state = OrganizerRole.EVENT_LEADER
        else:
            self.organizer.state = OrganizerRole.OC
        self.organizer.save()
        return HttpResponseRedirect(reverse('events:event-detail', args=[self.event.id]))
    
    def get_object(self, queryset=None):
        return get_object_or_404(Organizer, pk=self.kwargs.get("pko"))
    

    def get_success_url(self):
        return reverse('events:event-detail', args=[self.event.id])

class AddOrganizerView(EnsurePrivilegedUserViewMixin,
    SuccessMessageMixin,
    HtmxFormViewMixin,
    AjaxViewMixin,
    CreateView):

    ajax_template_name = "events/parts/add_organizer_form.html"
    template_name = "fiestaforms/pages/card_page_for_ajax_form.html"
    form_class = OrganizerForm
    model = Organizer
    
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.event = get_object_or_404(Event, pk=self.kwargs.get("pk"))
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        form_url = reverse_lazy('events:organizer-add', args=[self.event.id])

        context['form_url'] = form_url
        return context

    def get_initial(self):
        return {
            "event": self.event
        }
    
    def form_valid(self, form) -> HttpResponse:
        response = super().form_valid(form)

        form.save()
        return response
    
    def get_success_url(self):
        return reverse('events:event-detail', args=[self.event.id])
    
class DeleteOrganizerView(EnsurePrivilegedUserViewMixin,
    SuccessMessageMixin,
    DeleteView):
    
    request: HttpRequest
    model = Organizer
    template_name = "events/organizers_view.html"

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.event = get_object_or_404(Event, pk=self.kwargs.get("pk"))
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(Organizer, pk=self.kwargs.get("pko"))
    
    @transaction.atomic
    def delete(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        self.get_object().delete()
        return HttpResponse('')

    def get_success_url(self):
        return reverse("events:event-detail", args=[self.kwargs.get("pk")])

