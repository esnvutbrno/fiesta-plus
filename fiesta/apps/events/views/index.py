from django.views.generic import TemplateView


class EventsIndexView(TemplateView):
    template_name = 'events/index.html'

    