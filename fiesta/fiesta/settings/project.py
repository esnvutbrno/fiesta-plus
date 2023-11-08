from __future__ import annotations

from pathlib import Path

from ._utils import PathValue


class ProjectConfigMixin:
    BASE_DIR = PathValue(Path(__file__).resolve().parent.parent.parent)

    DEBUG = False

    DEBUG_PROPAGATE_EXCEPTIONS = False

    DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

    SITE_ID = 1
    LANGUAGE_CODE = "en-gb"

    TIME_ZONE = "UTC"

    USE_I18N = True

    USE_L10N = True

    USE_TZ = True

    FILTERS_EMPTY_CHOICE_LABEL = "---"

    WSGI_APPLICATION = "fiesta.wsgi.application"

    ROOT_URLCONF = "fiesta.urls"

    ROOT_DOMAIN = "fiesta.test"  # TODO: fill from environ

    def ALLOWED_HOSTS(self):
        return [f".{self.ROOT_DOMAIN}"]

    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    INSTALLED_APPS = [
        # dj admin autocompletion widgets, must be before admin
        "dal",
        "dal_select2",
        # Django native
        "django.contrib.admin",
        "phonenumber_field",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django.contrib.sites",
        "django.contrib.humanize",
        "django.forms",
        # Django 3rd party
        "polymorphic",
        "webpack_loader",
        "django_htmx",
        "django_tables2",
        "django_filters",
        "django_watchfiles",
        # Fiesta apps
        "apps.accounts.apps.AccountsConfig",
        "apps.buddy_system.apps.BuddySystemConfig",
        "apps.dashboard.apps.DashboardConfig",
        "apps.esncards.apps.ESNcardsConfig",
        "apps.fiestaforms.apps.FiestaFormsConfig",
        "apps.fiestarequests.apps.FiestaRequestsConfig",
        "apps.fiestatables.apps.FiestaTablesConfig",
        "apps.pages.apps.PagesConfig",
        "apps.events.apps.EventsConfig",
        "apps.plugins.apps.PluginsConfig",
        "apps.public.apps.PublicConfig",
        "apps.sections.apps.SectionsConfig",
        "apps.universities.apps.UniversitiesConfig",
        "apps.utils.apps.UtilsConfig",
        "apps.wiki.apps.WikiConfig",
        # Debugs
        "django_extensions",
        # django-allauth
        "allauth",
        "allauth.account",
        "allauth.socialaccount",
        "apps.esnaccounts",  # cannot have full config Path, since allauth/socialaccount/providers/__init__.py:38 sucks
        # "allauth.socialaccount.providers.facebook",  # NOTE: cannot be enabled BEFORE adding SocialApp, otherwise throws an error
        # "allauth.socialaccount.providers.google",
        # "allauth.socialaccount.providers.apple",
        # "allauth.socialaccount.providers.github",
        "allauth_cas",
        # superuser can log in as any user
        "loginas",
        # editorjs integration
        "django_editorjs_fields",
        "mptt",
        # health checks
        "health_check",
        "health_check.contrib.migrations",
    ]

    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        # admin needs it
        "django.contrib.messages.middleware.MessageMiddleware",
        # TODO: replace by CSP
        # "django.middleware.clickjacking.XFrameOptionsMiddleware",
        # 3rd party
        "django_htmx.middleware.HtmxMiddleware",
        # custom Fiesta, they're dependent on each other, so be careful
        "apps.sections.middleware.section_space.SectionSpaceMiddleware",
        "apps.sections.middleware.user_membership.UserMembershipMiddleware",
        "apps.plugins.middleware.plugin.CurrentPluginMiddleware",
        "apps.accounts.middleware.user_profile.UserProfileMiddleware",
    ]
