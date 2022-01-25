from django.utils.translation import gettext_lazy as _

from apps.plugins.models import BasePluginConfiguration


class SectionsConfiguration(BasePluginConfiguration):
    class Meta:
        verbose_name = _("sections configuration")
        verbose_name_plural = _("sections configurations")


__all__ = ["SectionsConfiguration"]
