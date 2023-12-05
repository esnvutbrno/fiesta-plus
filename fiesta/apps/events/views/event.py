import json
from typing import Any
from uuid import UUID
from django import http
from django.db import models
from django.forms.models import BaseModelForm

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
import requests


import django_filters
from django.contrib.postgres.search import SearchVector
from django.forms import TextInput
from django.views.generic import CreateView, DetailView, UpdateView, View
import django_tables2 as tables

from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django_filters import CharFilter, ChoiceFilter

from ..models import Participant, Organizer
from ..models.event import Event
from apps.utils.views import AjaxViewMixin
from apps.fiestaforms.views.htmx import HtmxFormViewMixin
from django.contrib.messages.views import SuccessMessageMixin
from apps.plugins.middleware.plugin import HttpRequest
from apps.events.forms.event import AddEventForm
from apps.events.models.price_variant import EventPriceVariantType

from ...fiestatables.columns import ImageColumn, NaturalDatetimeColumn, LabeledChoicesColumn
from ...fiestatables.filters import BaseFilterSet, ProperDateFromToRangeFilter
from ...fiestatables.views.tables import FiestaTableView
from ...sections.views.mixins.membership import EnsurePrivilegedUserViewMixin, EnsureLocalUserViewMixin, EnsureInternationalUserViewMixin
from ...sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin
from ...utils.breadcrumbs import with_breadcrumb, with_plugin_home_breadcrumb, with_object_breadcrumb
from allauth.account.utils import get_next_redirect_url
from django.contrib.auth import REDIRECT_FIELD_NAME



@with_plugin_home_breadcrumb
@with_breadcrumb(_("Add"))
class AddEventView(
    EnsurePrivilegedUserViewMixin,
    EnsureLocalUserViewMixin,
    EnsureInSectionSpaceViewMixin,
    CreateView,
    HtmxFormViewMixin,
    AjaxViewMixin,
    SuccessMessageMixin
):
    request: HttpRequest
    object: Event

    template_name = "fiestaforms/pages/card_page_for_ajax_form.html"
    ajax_template_name = "fiestaforms/parts/ajax-form-container.html"

    form_class = AddEventForm

    success_message = _("Event added")

    def get_initial(self):
        return dict(
            section=self.request.in_space_of_section,
            author=self.request.user
        )

    def get_success_url(self):
        return reverse("events:index")


@with_plugin_home_breadcrumb
@with_breadcrumb(_("Update"))
class UpdateEventView(
    EnsurePrivilegedUserViewMixin,
    EnsureLocalUserViewMixin,
    EnsureInSectionSpaceViewMixin,
    UpdateView,
    HtmxFormViewMixin,
    AjaxViewMixin,
    SuccessMessageMixin
):
    request: HttpRequest
    object: Event

    form_class = AddEventForm
    template_name = "fiestaforms/pages/card_page_for_ajax_form.html"
    ajax_template_name = "events/templates/parts/update_event_form.html"

    success_message = _("Event updated")

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.event = get_object_or_404(Event, pk=self.kwargs.get("pk"))
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        return dict(
            section=self.request.in_space_of_section,
        )

    def get_object(self, queryset=None):
        return self.request.in_space_of_section.events.get(id=self.event.pk)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(
            {
                "redirect_field_name": REDIRECT_FIELD_NAME,
                "redirect_field_value": get_next_redirect_url(self.request, REDIRECT_FIELD_NAME),
            }
        )
        return data

    def get_success_url(self):
        return reverse("events:event-detail", args=[self.object.id])


@with_plugin_home_breadcrumb
@with_breadcrumb(_("Detail"))
class EventDetailView(
    EnsureInSectionSpaceViewMixin, 
    DetailView, 
    SuccessMessageMixin, 
    HtmxFormViewMixin,
    AjaxViewMixin):
    
    request: HttpRequest
    object: Event

    model = Event
    template_name = 'events/event_detail.html'

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.event = get_object_or_404(Event, pk=self.kwargs.get("pk"))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        organizers_data = [{'name': organizer.user.get_full_name()} for organizer in self.event.event_organizers.all()]
        print(organizers_data)
        context['event'] = self.event
        context['organizers_json'] = json.dumps(organizers_data)
        context['organizer_roles'] = Organizer.Role.choices
        return context

class EventParticipantsFilter(BaseFilterSet):
    search = CharFilter(
        method="filter_search",
        label=_("Search"),
        widget=TextInput(attrs={"placeholder": _("Petr, Daniel...")}),
    )
    state = ChoiceFilter(choices=Participant.State.choices, label=_("State"))

    created = ProperDateFromToRangeFilter(label=_("Created"))

    class Meta(BaseFilterSet.Meta):
        pass

    def filter_search(self, queryset, name, value):
        return queryset.annotate(search=SearchVector("user__last_name", "user__first_name", "state")).filter(
            search=value
        )


class EventParticipantsTable(tables.Table):
    created = tables.DateTimeColumn(
        verbose_name=_("Created at"),
        format="SHORT_DATETIME_FORMAT",
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
    price__name = tables.Column(
        verbose_name=_("Price"),
        accessor="price.name",
        attrs={"th": {"class": "text-center"}},
    )
    state = tables.Column(
        verbose_name=_("State"),
        accessor="get_state_display",
        order_by="state",
        attrs={"th": {"class": "text-center"}},
    )

    class Meta:
        model = Participant

        fields = ("created",)

        sequence = (
            "user__full_name",
            "event__title",
            "price__name",
            "state"
        )

        empty_text = _("There are no participants")

    def render_created(self, value):
        return value.strftime("SHORT_DATETIME_FORMAT")

    def render_price__name(self, value):
        return str(value)


@with_plugin_home_breadcrumb
@with_breadcrumb(_("Participants"))
class ParticipantsView(
    EnsurePrivilegedUserViewMixin,
    EnsureLocalUserViewMixin, 
    EnsureInSectionSpaceViewMixin, 
    FiestaTableView):
    
    request: HttpRequest
    template_name = "fiestatables/page.html"
    table_class = EventParticipantsTable
    filterset_class = EventParticipantsFilter
    model = Participant

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.event = get_object_or_404(Event, pk=self.kwargs.get("pk"))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.in_space_of_section.events.get(id=self.event.pk).participants.filter(
            state__in=(
                Participant.State.WAITING,
                Participant.State.CONFIRMED,
                Participant.State.DELETED,
            )
        )


class EventParticipantRegister(
    EnsureInSectionSpaceViewMixin, 
    CreateView):
    
    model = Participant

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        Participant.objects.create(
            user=self.request.user,

        )
        return super().form_valid(form)
    
