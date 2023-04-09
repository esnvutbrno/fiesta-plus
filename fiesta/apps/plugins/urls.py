from django.urls import path

from apps.plugins.views.admin import AppAutocomplete, ConfigurationAutocomplete

app_name = "plugins"
urlpatterns = [
    path(
        "configuration-autocomplete",
        ConfigurationAutocomplete.as_view(),
        name="configuration-autocomplete",
    ),
    path(
        "app-autocomplete",
        AppAutocomplete.as_view(),
        name="app-autocomplete",
    ),
]
