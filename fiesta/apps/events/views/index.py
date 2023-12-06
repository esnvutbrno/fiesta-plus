from django.views.generic import ListView

from apps.events.models import Event, Participant
from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin
from apps.utils.breadcrumbs import with_breadcrumb
from django.utils.translation import gettext_lazy as _


@with_breadcrumb(_("Events"))
class EventsIndexView(EnsureInSectionSpaceViewMixin, ListView):
    template_name = 'events/index.html'
    model = Event

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['users_events'] = Event.objects.filter(event_participants__user=self.request.membership.user).order_by('start')
        
        context['upcoming_events'] = Event.objects.filter(section=self.request.in_space_of_section, state=Event.State.PUBLISHED).exclude(event_participants__user=self.request.membership.user).order_by('start')

        context['darft_events'] = Event.objects.filter(section=self.request.in_space_of_section, state=Event.State.DRAFT).order_by('start')
        return context