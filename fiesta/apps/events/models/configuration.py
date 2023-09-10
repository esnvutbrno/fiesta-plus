from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.plugins.models import BasePluginConfiguration


class EventsConfiguration(BasePluginConfiguration):
    require_confirmation = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('events configuration')
        verbose_name_plural = _('events configurations')


__all__ = ['EventsConfiguration']

# TODO can be created by
# TODO can be confirmed by
