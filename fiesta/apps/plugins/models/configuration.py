from django.db import models

from apps.utils.models import BasePolymorphicModel


class BasePluginConfiguration(BasePolymorphicModel):
    """
    Base configuration model for plugins.
    Usually it's extended and used for configuring running plugin.

    Cannot be abstract, since `Plugin.configuration` is pointing at it.
    """

    name = models.CharField(max_length=64, default="default")

    def __str__(self):
        return f"{self.polymorphic_ctype.name if self.polymorphic_ctype else '---'}: {self.name}"


__all__ = ["BasePluginConfiguration"]
