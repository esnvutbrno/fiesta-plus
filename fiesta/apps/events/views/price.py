from uuid import UUID

import django_filters
from django.contrib.postgres.search import SearchVector
from django.forms import TextInput
from django.views.generic import CreateView, DetailView, UpdateView
import django_tables2 as tables

from django.utils.translation import gettext_lazy as _
from django.urls import reverse, reverse_lazy
from django_filters import CharFilter, ChoiceFilter
from django_tables2 import Column
from django.db import models

from ..models import Participant
from ..models.price_variant import PriceVariant, EventPriceVariantType
from apps.utils.views import AjaxViewMixin
from apps.fiestaforms.views.htmx import HtmxFormMixin
from django.contrib.messages.views import SuccessMessageMixin
from apps.plugins.middleware.plugin import HttpRequest
from apps.events.forms.price import PriceForm
from apps.events.forms.event import AddEventForm, UpdateEventForm
from ..models.participant import ParticipantState
from ...fiestatables.columns import ImageColumn, NaturalDatetimeColumn, LabeledChoicesColumn
from ...fiestatables.filters import BaseFilterSet, ProperDateFromToRangeFilter
from ...fiestatables.views.tables import FiestaTableView
from ...sections.views.mixins.membership import EnsurePrivilegedUserViewMixin
from ...utils.breadcrumbs import with_breadcrumb
from allauth.account.utils import get_next_redirect_url
from django.contrib.auth import REDIRECT_FIELD_NAME

class PriceView(     
    EnsurePrivilegedUserViewMixin,
    SuccessMessageMixin,
    HtmxFormMixin,
    AjaxViewMixin,
    UpdateView,
):
    template_name = "events/price.html"
    ajax_template_name = "events/price_form.html"
    model = PriceVariant
    form_class = PriceForm

    success_url = reverse_lazy("events:event-update")
    success_message = _("Priced")