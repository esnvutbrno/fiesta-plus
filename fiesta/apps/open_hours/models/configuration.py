from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.plugins.models import BasePluginConfiguration


class OpenHoursConfiguration(BasePluginConfiguration):
    ...

    class Meta:
        verbose_name = _('open_hours configuration')
        verbose_name_plural = _('open_hours configurations')


__all__ = ['OpenHoursConfiguration']
