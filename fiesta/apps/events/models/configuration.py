from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.plugins.models import BasePluginConfiguration


class EventsConfiguration(BasePluginConfiguration):
    require_confirmation = models.BooleanField(
        default=True,
        verbose_name=_("require confirmation to publish"),
    )

    members_can_create = models.BooleanField(
        default=True,
        verbose_name=_("basic members can create an event"),
    )

    online_purchases = models.BooleanField(
        default=True,
        verbose_name=_("online purchases"),
    )

    class Meta:
        verbose_name = _('events configuration')
        verbose_name_plural = _('events configurations')


__all__ = ['EventsConfiguration']
