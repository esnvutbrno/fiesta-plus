from django.urls import path

# Define your urls here
from django.views.generic import TemplateView

urlpatterns = [path("", TemplateView.as_view(template_name="accounts/main.html"))]
