from __future__ import annotations

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from apps.plugins.utils import all_plugin_apps

admin.site.site_title = _("Buena Fiesta admin")
admin.site.site_header = _("Buena Fiesta")
admin.site.index_title = _("Site administration")

handler403 = "fiesta.views.handler_403"

urlpatterns = [
    path(
        # url prefix for all plugin-apps
        route=app.url_prefix,
        # included with namespace
        view=include((app.urlpatterns, app.label)),
    )
    for app in all_plugin_apps()
] + [
    path("", include("apps.public.urls", namespace="public")),
    path("admin/", include("loginas.urls")),
    path("admin/", admin.site.urls),
    # wiki is not plugin (yet)
    path("docs/", include("apps.wiki.urls", namespace="wiki")),
    # for serving files
    path("files/", include("apps.files.urls", namespace="files")),
    # for plugins views (autocomplete etc)
    path("plugins/", include("apps.plugins.urls", namespace="plugins")),
    # handling users/profiles/memberships
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
    # handling authentication (including social auth)
    path("auth/", include("allauth.urls")),
    path("auto-options/", include("django_select2.urls")),
    # wagtail related
    path("cms/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),  # TODO: needed?
    path("pages/", include(wagtail_urls)),
]

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
