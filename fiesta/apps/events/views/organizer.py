from typing import Any

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404



from django.views.generic import CreateView, DeleteView, View


from django.utils.translation import gettext_lazy as _
from django.urls import reverse, reverse_lazy


from ..models.event import Event
from apps.utils.views import AjaxViewMixin
from apps.fiestaforms.views.htmx import HtmxFormViewMixin
from django.contrib.messages.views import SuccessMessageMixin
from apps.plugins.middleware.plugin import HttpRequest


from ..models.organizer import Organizer, OrganizerRole
from apps.events.forms.organizer import OrganizerForm
from ...sections.views.mixins.membership import EnsurePrivilegedUserViewMixin
from ...utils.breadcrumbs import with_breadcrumb
from allauth.account.utils import get_next_redirect_url


class UpdateOrganizerRole(AjaxViewMixin, SuccessMessageMixin, HtmxFormViewMixin ,EnsurePrivilegedUserViewMixin, View):
    model = Organizer
    
    def dispatch(self, request, *args, **kwargs):
        self.event = get_object_or_404(Event, pk=self.kwargs.get("pk"))
        self.organizer = get_object_or_404(Organizer, pk=self.kwargs.get("pko"))
        return super().dispatch(request, *args, **kwargs)
    

    def post(self, request, pk, pko):
        if request.POST.get('role') == "event_leader":
            self.organizer.role = OrganizerRole.EVENT_LEADER
        else:
            self.organizer.role = OrganizerRole.OC
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
    
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        self.get_object().delete()
        return HttpResponse('')

    def get_success_url(self):
        return reverse("events:event-detail", args=[self.kwargs.get("pk")])

