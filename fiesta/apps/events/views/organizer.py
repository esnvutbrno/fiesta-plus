from typing import Any

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404



from django.views.generic import CreateView, DeleteView, UpdateView


from django.utils.translation import gettext_lazy as _
from django.urls import reverse, reverse_lazy


from ..models.event import Event
from apps.utils.views import AjaxViewMixin
from apps.fiestaforms.views.htmx import HtmxFormViewMixin
from django.contrib.messages.views import SuccessMessageMixin
from apps.plugins.middleware.plugin import HttpRequest


from ..models.organizer import Organizer
from apps.events.forms.organizer import OrganizerForm
from ...sections.views.mixins.membership import EnsurePrivilegedUserViewMixin
from ...sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin
from ...utils.breadcrumbs import with_breadcrumb
from allauth.account.utils import get_next_redirect_url


class UpdateOrganizerRole(
    AjaxViewMixin, 
    SuccessMessageMixin, 
    HtmxFormViewMixin,
    EnsurePrivilegedUserViewMixin, 
    EnsureInSectionSpaceViewMixin,
    UpdateView):
    fields = ['role']
    model = Organizer
    
    def dispatch(self, request, *args, **kwargs):
        self.event = get_object_or_404(Event, pk=self.kwargs.get("pk"))
        self.organizer = get_object_or_404(Organizer, pk=self.kwargs.get("pko"))
        return super().dispatch(request, *args, **kwargs)
    

    # def post(self, request, pk, pko):
    #     if request.POST.get('role') == "event_leader":
    #         self.organizer.role = Organizer.Role.EVENT_LEADER
    #     else:
    #         self.organizer.role = Organizer.Role.OC
    #     self.organizer.save()
    #     return HttpResponseRedirect(reverse('events:event-detail', args=[self.event.id]))
    
    
    def get_object(self, queryset=None):
        return get_object_or_404(Organizer, pk=self.kwargs.get("pko"))
    

    def get_success_url(self):
        return reverse('events:event-detail', args=[self.event.id])

class AddOrganizerView(EnsurePrivilegedUserViewMixin,
    EnsureInSectionSpaceViewMixin,
    SuccessMessageMixin,
    HtmxFormViewMixin,
    AjaxViewMixin,
    CreateView):

    ajax_template_name = "fiestaforms/parts/ajax-form-container.html"
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
    
    def get_success_url(self):
        return reverse('events:event-detail', args=[self.event.id])
    
class DeleteOrganizerView(EnsurePrivilegedUserViewMixin,
    EnsureInSectionSpaceViewMixin,
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
        return reverse("events:event-detail", args=[self.kwargs.get("pk")])

