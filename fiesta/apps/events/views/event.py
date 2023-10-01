from uuid import UUID

import django_filters
from django.contrib.postgres.search import SearchVector
from django.forms import TextInput
from django.views.generic import CreateView, DetailView
import django_tables2 as tables

from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django_filters import CharFilter, ChoiceFilter
from django_tables2 import Column
from django.db import models

from ..models import Participant
from ..models.event import Event
from apps.utils.views import AjaxViewMixin
from apps.fiestaforms.views.htmx import HtmxFormMixin
from django.contrib.messages.views import SuccessMessageMixin
from apps.plugins.middleware.plugin import HttpRequest
from apps.events.forms.event import AddEventForm
from ..models.participant import ParticipantState
from ...fiestatables.columns import ImageColumn, NaturalDatetimeColumn, LabeledChoicesColumn
from ...fiestatables.filters import BaseFilterSet, ProperDateFromToRangeFilter
from ...fiestatables.views.tables import FiestaTableView
from ...sections.views.mixins.membership import EnsurePrivilegedUserViewMixin
from ...utils.breadcrumbs import with_breadcrumb


@with_breadcrumb(_("Events"))
@with_breadcrumb(_("Add"))
class AddEventView(
    CreateView,
    HtmxFormMixin,
    AjaxViewMixin,
    SuccessMessageMixin
):
    request: HttpRequest
    object: Event

    template_name = 'events/add_event.html'
    ajax_template_name = 'events/parts/add_event_form.html'

    form_class = AddEventForm

    success_message = _("Event added")

    def get_initial(self):
        print(self.request.in_space_of_section.id)
        return dict(
            section=self.request.in_space_of_section,
        )

    def get_success_url(self):
        return reverse("events:index")


@with_breadcrumb(_("Events"))
@with_breadcrumb(_("Detail"))
class EventDetailView(DetailView):
    request: HttpRequest
    object: Event

    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'



class EventParticipantsTable(tables.Table):
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
        template_name = "fiestatables/page.html"
        attrs = {"class": "table table-bordered table-striped table-hover"}
        empty_text = _("No p Applications")


    def render_created(self, value):
        return value.strftime("%d/%m/%Y %H:%M:%S")

    def render_price__name(self, value):
        return str(value)


@with_breadcrumb(_("Events"))
@with_breadcrumb(_("participants"))
class ParticipantsView(EnsurePrivilegedUserViewMixin, FiestaTableView, DetailView):
    request: HttpRequest
    object: Event
    template_name = "fiestatables/page.html"
    table_class = EventParticipantsTable
    # filterset_class = EventParticipantsFilter
    model = Event
    context_object_name = 'event'

    def get_queryset(self, event):
        return self.request.in_space_of_section.esncard_applications.filter(
            state__in=(
                ParticipantState.WAITING,
                ParticipantState.CONFIRMED,
                ParticipantState.DELETED,
            )
        ).select_related("participant")
