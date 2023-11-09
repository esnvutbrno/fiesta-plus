from django.views.generic import ListView

from apps.events.models import Event
from apps.events.models.participant import ParticipantState


class EventsIndexView(ListView):
    template_name = 'events/index.html'
    model = Event

    def get_queryset(self):
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the user's confirmed participants
        participating = self.request.user.participants.filter(state=ParticipantState.CONFIRMED)

        # Add the confirmed participants to the context
        context['participating'] = participating

        return context