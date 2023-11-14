from __future__ import annotations

from django.urls import path

from apps.public.views import PublicTeamView, RootPageView

app_name = "public"
urlpatterns = [
    path(
        "",
        RootPageView.as_view(),
        name="home",
    ),
    path(
        "team",
        PublicTeamView.as_view(),
        name="team",
    ),
]
