from django.views.generic import TemplateView


class BuddySystemIndexView(TemplateView):
    template_name = "buddy_system/index.html"
