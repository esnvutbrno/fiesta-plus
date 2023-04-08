from django.urls import path

from apps.public.views import PublicHomepageView, PublicTeamView

app_name = "public"
urlpatterns = [
    path(
        "",
        PublicHomepageView.as_view(),
        name="home",
    ),
    path(
        "team",
        PublicTeamView.as_view(),
        name="team",
    ),
]
