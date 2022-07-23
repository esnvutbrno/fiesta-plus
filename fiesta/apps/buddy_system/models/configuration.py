from django.utils.translation import gettext_lazy as _

from apps.plugins.models import BasePluginConfiguration


class BuddySystemConfiguration(BasePluginConfiguration):
    ...

    class Meta:
        verbose_name = _('buddy system configuration')
        verbose_name_plural = _('buddy system configurations')


__all__ = ['BuddySystemConfiguration']
