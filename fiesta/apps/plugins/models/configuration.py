from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_lifecycle import LifecycleModelMixin

from apps.utils.models import BasePolymorphicModel


class BasePluginConfiguration(LifecycleModelMixin, BasePolymorphicModel):
    """
    Base configuration model for plugins.
    Usually it's extended and used for configuring running plugin.

    Unfortunately cannot be abstract, since `Plugin.configuration` is pointing at it.
    """

    name = models.CharField(
        max_length=64,
        default="default",
        verbose_name=_("human readable name"),
    )

    section = models.ForeignKey(
        "sections.Section",
        null=True,
        blank=True,
        verbose_name=_("owner section"),
        on_delete=models.RESTRICT,
        db_index=True,
    )

    shared = models.BooleanField(
        default=False,
        verbose_name=_("is available to share between sections"),
    )

    class Meta:
        verbose_name = _("base configuration")
        verbose_name_plural = _("base configurations")

    def __str__(self):
        return (
            f"{self.polymorphic_ctype.name if self.polymorphic_ctype else '---'}: "
            f"{_('🔗') if self.shared else ''}"
            f"{self.section if self.section else ''}" + f" ({self.name})"
            if self.name
            else ""
        )

    def clean(self):
        # cannot use isinstance, since children are allowed to create
        if type(self) == BasePluginConfiguration:
            raise ValidationError(
                _("Base plugin configuration cannot be saved directly, only children.")
            )


__all__ = ["BasePluginConfiguration"]
