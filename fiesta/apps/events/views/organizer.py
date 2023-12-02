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
from apps.events.forms.organizer import OrganizerForm, OrganizerRoleForm
from django.utils.html import format_html
from django.http import JsonResponse


class EventOrganizersFilter(BaseFilterSet):
    search = CharFilter(
        method="filter_search",
        label=_("Search"),
        widget=TextInput(attrs={"placeholder": _("Petr, Daniel...")}),
    )
    state = ChoiceFilter(choices=OrganizerRole.choices, label=_("Role"))

    created = ProperDateFromToRangeFilter(label=_("Created"))

    class Meta(BaseFilterSet.Meta):
        pass

    def filter_search(self, queryset, name, value):
        return queryset.annotate(search=SearchVector("user__last_name", "user__first_name", "role")).filter(
            search=value
        )



class EventOrganizersTable(tables.Table):
    created = tables.DateTimeColumn(
        verbose_name=_("Created at"),
        format="d/m/Y H:i:s",
        attrs={"th": {"class": "text-center"}},
    )
    user__full_name = tables.Column(
        verbose_name=_("User"),
        accessor="user.get_full_name",
        order_by=("user__last_name", "user__first_name"),
        attrs={"th": {"class": "text-center"}},
    )
    event__title = tables.Column(
        verbose_name=_("Event"),
        accessor="event.title",
        attrs={"th": {"class": "text-center"}},
    )
    # role = tables.Column(
    #     verbose_name=_("Role"),
    #     accessor="state",
    #     attrs={"th": {"class": "text-center"}},
    # )
    role = tables.TemplateColumn(
        template_name="events/parts/update_role_organizer_dropdown.html",
        verbose_name=_("Role"),
        orderable=False,  # Since this is a form element, you might want to make it unsortable
    )
    
    remove = tables.TemplateColumn(
        template_name="events/parts/delete_organizer_button.html",
        verbose_name=_("Remove"),
        orderable=False,  # Since this is a form element, you might want to make it unsortable
    )
    


    class Meta:
        model = Organizer

        fields = ("created",)
                  
        sequence = (
            "user__full_name",
            "event__title",
            "role",
            "remove",
        )

        empty_text = _("No organizers")


    def render_created(self, value):
        return value.strftime("%d/%m/%Y %H:%M:%S")

    def render_price__name(self, value):
        return str(value)


class OrganizersView(EnsurePrivilegedUserViewMixin, FiestaTableView, ListView):
    request: HttpRequest
    template_name = "events/organizers_view.html"
    table_class = EventOrganizersTable
    filterset_class = EventOrganizersFilter
    model = Organizer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organizer_roles'] = OrganizerRole.choices
        context['event'] = self.event
        return context
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.event = get_object_or_404(Event, pk=self.kwargs.get("pk"))
        return super().dispatch(request, *args, **kwargs)
    def get_queryset(self):
        return self.request.in_space_of_section.events.get(id=self.event.pk).organizers.filter(
            state__in=(
                OrganizerRole.OC,
                OrganizerRole.EVENT_LEADER,
            )
        )

class UpdateOrganizerRole(AjaxViewMixin, SuccessMessageMixin, HtmxFormViewMixin ,EnsurePrivilegedUserViewMixin, View):
    model = Organizer
    # ajax_template_name = "events/parts/update_role_organizer_dropdown.html"
    # template_name = "events/organizers_view.html"
    # form_class = OrganizerRoleForm
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
        return HttpResponseRedirect(reverse('events:organizers', args=[self.event.id]))
    
    def get_object(self, queryset=None):
        return get_object_or_404(Organizer, pk=self.kwargs.get("pko"))
    

    def get_success_url(self):
        return reverse('events:organizers', args=[self.event.id])

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
        return reverse('events:organizers', args=[self.event.id])
    
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

    def get_success_url(self):
        return reverse("events:organizers", args=[self.kwargs.get("pk")])

