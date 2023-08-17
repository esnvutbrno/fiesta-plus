from django.views.generic import TemplateView


class OpenHoursIndexView(TemplateView):
    template_name = 'open_hours/index.html'
