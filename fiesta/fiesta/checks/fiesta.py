"""Checks related to project, usually to keep codestyle."""
import django

from django.apps import AppConfig, apps
from django.core import checks


def check_app(app: AppConfig):
    if "_" in app.name and "_system" not in app.name:
        yield django.core.checks.Warning(
            "App name contains an underscore",
            hint="Rename the application to keep Django style.",
            obj=app.name,
            id="F001",
        )

    # it's not much but it's an honest work
    if (
        len(app.name.rpartition(".")[-1]) > 4
        and not app.name.endswith("s")
        and "_system" not in app.name
        and "public" not in app.name
        and "dashboard" not in app.name
    ):
        yield django.core.checks.Warning(
            "App name is singular",
            hint="Make the app name plural.",
            obj=app.name,
            id="F002",
        )


@checks.register(checks.files)
def check_models(app_configs, **kwargs):
    errors = []
    for app in apps.get_app_configs():  # type: AppConfig
        # Skip third party apps.
        if "site-packages" in app.path:
            continue

        for error in check_app(app):
            errors.append(error)

    return errors
