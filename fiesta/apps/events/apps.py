from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from apps.plugins.plugin import BasePluginAppConfig


class EventsConfig(BasePluginAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.events"
    verbose_name = _("Events")
    emoji = "🗓️"
    description = _("Fiesta plugin to handle events management and registrations.")
    order = 50

    configuration_model = "events.EventsConfiguration"

    feature_state = BasePluginAppConfig.FeatureState.EXPERIMENTAL


__all__ = ["EventsConfig"]
