from django.utils.translation import gettext_lazy as _

from apps.fiestarequests.models import BaseRequestSystemConfiguration


class BuddySystemConfiguration(BaseRequestSystemConfiguration):
    ...

    class Meta:
        verbose_name = _('buddy system configuration')
        verbose_name_plural = _('buddy system configurations')


__all__ = ['BuddySystemConfiguration']
