from django.views.generic import TemplateView


class MembershipView(TemplateView):
    template_name = "accounts/membership.html"
