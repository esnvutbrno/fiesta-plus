from django.views.generic import ListView

from apps.events.models import Event


class EventsIndexView(ListView):
    template_name = 'events/index.html'
    model = Event

    def get_queryset(self):
        return super().get_queryset()
