from django.urls import path

from .views import WikiView

app_name = "wiki"
urlpatterns = [
    path("", WikiView.as_view(), name="index"),
    path("<path:path>", WikiView.as_view()),
]
