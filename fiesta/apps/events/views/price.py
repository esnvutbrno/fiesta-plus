from typing import Any
from uuid import UUID
from django import http

from django.http import HttpRequest, HttpResponse


from django.views.generic import CreateView, UpdateView, DeleteView

from django.utils.translation import gettext_lazy as _
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404

from ..models import Event
from ..models.price_variant import PriceVariant
from apps.utils.views import AjaxViewMixin
from apps.fiestaforms.views.htmx import HtmxFormViewMixin
from django.contrib.messages.views import SuccessMessageMixin
from apps.plugins.middleware.plugin import HttpRequest
from apps.events.forms.price import PriceForm

from ...sections.views.mixins.membership import EnsurePrivilegedUserViewMixin
from ...sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin
from ...utils.breadcrumbs import with_breadcrumb
from allauth.account.utils import get_next_redirect_url
from django.db import transaction
from django.contrib.auth import REDIRECT_FIELD_NAME


class PriceView(
    EnsureInSectionSpaceViewMixin,
    SuccessMessageMixin,
    HtmxFormViewMixin,
    AjaxViewMixin,
    CreateView,
):
    template_name = "fiestaforms/pages/card_page_for_ajax_form.html"
    ajax_template_name = "events/parts/price_form.html"
    model = Event
    form_class = PriceForm
    success_message = _("Priced")
    
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.event = get_object_or_404(Event, pk=self.kwargs.get("pk"))
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_url"] = reverse_lazy("events:price", kwargs={"pk": self.event.pk})
        
        return context

    def get_initial(self):
        return {
            "event": self.event,
        }
    
    def get_success_url(self):
        return reverse("events:event-detail", args=[self.event.pk])

    def form_valid(self, form):
        response = super().form_valid(form)
        
        PriceVariant.objects.get_or_create(
            event=self.event,
            type=form.instance.type,
        )

        return response

class PriceUpdate(
    EnsurePrivilegedUserViewMixin,
    SuccessMessageMixin,
    HtmxFormViewMixin,
    AjaxViewMixin,
    UpdateView,
):
    template_name = "fiestaforms/pages/card_page_for_ajax_form.html"
    ajax_template_name = "events/parts/update_price_form.html"
    model = Event
    form_class = PriceForm

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.event = get_object_or_404(Event, pk=self.kwargs.get("pk"))
        self.price = get_object_or_404(PriceVariant, pk=self.kwargs.get("pricepk"))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_url"] = reverse_lazy("events:price-update", kwargs={"pk": self.event.pk, "pricepk": self.price.pk})
        
        return context
    
    def get_object(self, queryset=None) -> PriceVariant:
        price_pk = self.kwargs.get('pricepk')
        return get_object_or_404(PriceVariant, pk=price_pk)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        form.save() 
        return response
    
    def get_success_url(self):
        return reverse("events:event-detail", args=[self.event.pk])
    
class PriceDelete(
    EnsurePrivilegedUserViewMixin,
    SuccessMessageMixin,
    HtmxFormViewMixin,
    AjaxViewMixin,
    DeleteView,
):
    model = Event
    form_class = PriceForm
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.event = get_object_or_404(Event, pk=self.kwargs.get("pk"))
        self.price = get_object_or_404(PriceVariant, pk=self.kwargs.get("pricepk"))

        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_url"] = reverse_lazy("events:price-delete", kwargs={"pk": self.event.pk, "pricepk": self.price.pk})
        
        return context
    
    def get_object(self, queryset=None) -> PriceVariant:
        price_pk = self.kwargs.get('pricepk')

        return get_object_or_404(PriceVariant, pk=price_pk)

    @transaction.atomic
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        self.price.delete()
        return HttpResponse('')
    
    def get_success_url(self):
        return reverse("events:event-detail", args=[self.event.pk])
    