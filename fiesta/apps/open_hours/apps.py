from django.utils.translation import gettext_lazy as _
from apps.plugins.plugin import BasePluginAppConfig


class OpenHoursConfig(BasePluginAppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.open_hours'
    verbose_name = _('open_hours')
    emoji = ""
    description = _('open_hours is one of the plugins.')

    configuration_model = 'open_hours.OpenHoursConfiguration'


__all__ = ['OpenHoursConfig']
