from django.urls import path
from django.views.generic import TemplateView

from apps.accounts.views.profile import ProfileView

urlpatterns = [
    path("profile", ProfileView.as_view(), name="profile"),
    path("", TemplateView.as_view(template_name="accounts/index.html")),
]
