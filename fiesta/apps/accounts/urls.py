from django.urls import path
# Define your urls here
from django.views.generic import TemplateView

from apps.accounts.views.profile import ProfileView

urlpatterns = [
    path(
        "auth/login",
        TemplateView.as_view(template_name="accounts/auth/login.html"),
        name="login",
    ),
    path("profile", ProfileView.as_view()),
    path("", TemplateView.as_view(template_name="accounts/index.html")),
]
