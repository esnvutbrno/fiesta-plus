from django.views.generic import TemplateView


class WannaBuddyView(TemplateView):
    template_name = 'buddy_system/wanna_buddy.html'