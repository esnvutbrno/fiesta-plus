from django.urls import path

# Define your urls here
from django.views.generic import TemplateView

urlpatterns = [
    path(
        "auth/login",
        TemplateView.as_view(template_name="accounts/auth/login.html"),
        name="login",
    ),
    path("", TemplateView.as_view(template_name="accounts/index.html")),
]
