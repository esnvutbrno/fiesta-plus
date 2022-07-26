from django.views.generic import TemplateView

from apps.sections.middleware.section_space import HttpRequest


class BuddySystemIndexView(TemplateView):
    request: HttpRequest
    template_name = "buddy_system/index.html"
