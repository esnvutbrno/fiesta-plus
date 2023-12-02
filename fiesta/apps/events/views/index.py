from django.views.generic import ListView

from apps.events.models import Event
from apps.events.models.participant import ParticipantState
from apps.utils.breadcrumbs import with_breadcrumb
from django.utils.translation import gettext_lazy as _


@with_breadcrumb(_("Events"))
class EventsIndexView(ListView):
    template_name = 'events/index.html'
    model = Event

    def get_queryset(self):
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the user's confirmed participants
        participations = self.request.user.participants.filter(state=ParticipantState.CONFIRMED)

        # Add the confirmed participants to the context
        context['participations'] = participations

        return context