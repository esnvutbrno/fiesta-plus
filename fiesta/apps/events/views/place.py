from typing import Any


from django.http import HttpRequest, HttpResponse


from django.contrib.postgres.search import SearchVector
from django.forms import TextInput
from django.views.generic import CreateView, UpdateView, DeleteView
import django_tables2 as tables

from django.utils.translation import gettext_lazy as _
from django.urls import reverse, reverse_lazy
from django_filters import CharFilter

from django.db import models
from django.shortcuts import get_object_or_404

from ..models import Place

from apps.utils.views import AjaxViewMixin
from apps.fiestaforms.views.htmx import HtmxFormViewMixin
from django.contrib.messages.views import SuccessMessageMixin
from apps.plugins.middleware.plugin import HttpRequest
from apps.events.forms.place import PlaceForm

from ...fiestatables.filters import BaseFilterSet
from ...fiestatables.views.tables import FiestaTableView
from ...sections.views.mixins.membership import EnsurePrivilegedUserViewMixin
from ...sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin
from ...utils.breadcrumbs import with_breadcrumb
from allauth.account.utils import get_next_redirect_url
from django.db import transaction


class PlaceFilter(BaseFilterSet):
    search = CharFilter(
        method="filter_search",
        label=_("Search"),
        widget=TextInput(attrs={"placeholder": _("Petr, Daniel...")}),
    )

    class Meta(BaseFilterSet.Meta):
        pass

    def filter_search(self, queryset, name, value):
        return queryset.annotate(search=SearchVector("name")).filter(
            search=value
        )



class PlaceTable(tables.Table):
    name = tables.Column(
        verbose_name=_("Name"),
        accessor="name",
        attrs={"th": {"class": "text-center"}},
    )
    link = tables.Column(
        verbose_name=_("Link"),
        accessor="link",
        attrs={"th": {"class": "text-center"}},
    )
    map_link = tables.Column(
        verbose_name=_("Map"),
        accessor="map_link",
        attrs={"th": {"class": "text-center"}},
    )

    delete_button = tables.TemplateColumn(
        template_name="events/parts/delete_place_button.html",
        attrs={"th": {"class": "text-center"}},
        extra_context={'place': tables.A('pk')}
    )

    update_button = tables.TemplateColumn(
        template_name="events/parts/update_place_button.html",
        attrs={"th": {"class": "text-center"}},
        extra_context={'place': tables.A('pk')}
    )

    class Meta:
        model = Place
                  
        fields = ("created",)

        sequence = (
            "name",
            "link",
            "map_link"
        )


        empty_text = _("No places added yet")


    def render_place__name(self, value):
        return str(value)
    
class PlaceView(EnsurePrivilegedUserViewMixin,
    EnsureInSectionSpaceViewMixin,
    HtmxFormViewMixin,
    FiestaTableView
):
    template_name = "events/place_view.html"
    table_class = PlaceTable
    filterset_class = PlaceFilter
    model = Place

    context_object_name = "places"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        return self.request.in_space_of_section.places.all()

class AddPlaceView(EnsurePrivilegedUserViewMixin,
    EnsureInSectionSpaceViewMixin,
    SuccessMessageMixin,
    HtmxFormViewMixin,
    AjaxViewMixin,
    CreateView):

    template_name = "fiestaforms/pages/card_page_for_ajax_form.html"
    ajax_template_name = "fiestaforms/parts/ajax-form-container.html"
    
    form_class = PlaceForm
    model = Place

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if 'pk' in self.kwargs:
            form_url = reverse_lazy('events:eventplace-add', kwargs={'pk': self.kwargs['pk']})
        else:
            form_url = reverse_lazy('events:place-add')

        context['form_url'] = form_url
        return context

    def get_initial(self):
        return {
            "section": self.request.in_space_of_section
        }
    
    def get_success_url(self):
        if self.kwargs.get("pk") is not None:
            return reverse_lazy('events:event-update', args=[self.kwargs.get("pk")])
        return reverse_lazy('events:place')
    
class DeletePlaceView(EnsurePrivilegedUserViewMixin,
    EnsureInSectionSpaceViewMixin,
    SuccessMessageMixin,
    HtmxFormViewMixin,
    AjaxViewMixin,
    DeleteView):
    request: HttpRequest
    model = Place

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.place = get_object_or_404(Place, pk=self.kwargs.get("pk"))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('events:place')


class UpdatePlaceView(    
    EnsurePrivilegedUserViewMixin,
    EnsureInSectionSpaceViewMixin,
    SuccessMessageMixin,
    HtmxFormViewMixin,
    AjaxViewMixin,
    UpdateView,):
    
    template_name = "fiestaforms/pages/card_page_for_ajax_form.html"
    ajax_template_name = "fiestaforms/parts/ajax-form-container.html"

    model = Place
    form_class = PlaceForm

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.place = get_object_or_404(Place, pk=self.kwargs.get("pk"))
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["form_url"] = reverse_lazy('events:place-update', kwargs={'pk': self.kwargs['pk']})
        return context
    
    def get_object(self, queryset=None) -> Place:
        pk = self.kwargs.get('pk')
        return get_object_or_404(Place, pk=pk)
    
    def get_success_url(self):
        return reverse_lazy("events:place")
