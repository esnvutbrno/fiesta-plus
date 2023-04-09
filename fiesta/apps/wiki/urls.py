from django.urls import path

from .views import SearchWikiView, WikiView

app_name = "wiki"
urlpatterns = [
    path("search", SearchWikiView.as_view(), name="search"),
    path("", WikiView.as_view(), name="index"),
    path("<path:path>", WikiView.as_view(), name="page"),
]
