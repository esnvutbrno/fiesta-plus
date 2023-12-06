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

        participants = Participant.objects.filter(user=self.request.membership.user)

        events = [participant.event for participant in participants if participant.event]

        context['users_events'] = events

        return context