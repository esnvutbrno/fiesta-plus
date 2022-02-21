from pathlib import Path

from . import config


class AppConfigMixin:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    DEBUG = False
    SECRET_KEY = config("SECRET_KEY")

    DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

    SITE_ID = 1
    LANGUAGE_CODE = "en-us"

    TIME_ZONE = "UTC"

    USE_I18N = True

    USE_TZ = True

    ALLOWED_HOSTS: list[str] = [".localhost", "127.0.0.1"]

    WSGI_APPLICATION = "fiesta.wsgi.application"

    ROOT_URLCONF = "fiesta.urls"

    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    INSTALLED_APPS = [
        # Django native
        "django.contrib.admin",
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
        # Fiesta apps
        "apps.accounts.apps.AccountsConfig",
        "apps.esnaccounts",  # cannot have full config Path, since allauth/socialaccount/providers/__init__.py:38 sucks
        "apps.esncards.apps.ESNcardsConfig",
        "apps.fiestaforms.apps.FiestaformsConfig",
        "apps.plugins.apps.PluginsConfig",
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
        # "allauth.socialaccount.providers.facebook",
        "allauth_cas",
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
        # custom Fiesta
        "apps.sections.middleware.user_membership.UserMembershipMiddleware",
        "apps.plugins.middleware.plugin.CurrentPluginMiddleware",
        "apps.accounts.middleware.user_profile.UserProfileMiddleware",
    ]
