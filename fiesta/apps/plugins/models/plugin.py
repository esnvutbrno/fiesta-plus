from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..plugin import PluginAppConfig
from ..utils import all_plugins_as_choices
from apps.utils.models import BaseTimestampedModel


class Plugin(BaseTimestampedModel):
    class State(models.TextChoices):
        ENABLED = "enabled", _("enabled")
        READ_ONLY = "read_only", _("read-only")
        DISABLED = "disabled", _("disabled")
        # TODO: state with visibility only for editors and highers

    # section = models.ForeignKey(
    #     'core.Section',
    #     on_delete=models.CASCADE,
    #     related_name='plugins',
    # )

    state = models.CharField(
        choices=State.choices,
        default=State.ENABLED,
        max_length=16,
        verbose_name=_("Plugin state"),
        help_text=_(
            "Current state of plugin - affects, if plugin could be displayed by "
            "international/member/editor/admin/at all."
        ),
    )

    app_label = models.CharField(
        max_length=256,
        choices=all_plugins_as_choices(),
        verbose_name=_("App label"),
        help_text=_("Defines system application, which specific plugin represents."),
    )

    configuration = models.ForeignKey(
        "plugins.BasePluginConfiguration",
        on_delete=models.RESTRICT,
        related_name="plugin",
        null=True,
        blank=True,
        verbose_name=_("Plugin configuration"),
        help_text=_("Defines, in which configuration specific plugin runs."),
    )

    def clean(self) -> None:
        super().clean()

        if not self.configuration and not self.app_config.configuration_model:
            # not needed and not filled
            return
        elif self.configuration and not self.app_config.configuration_model:
            raise ValidationError(
                {"configuration": _("Selected plugin does not support configuration.")}
            )
        elif self.app_config.configuration_model and not self.configuration:
            raise ValidationError(
                {"configuration": _("Selected plugin does requires configuration.")},
                code="required",
            )

        expected_content_type = ContentType.objects.get_for_model(
            apps.get_model(self.app_config.configuration_model)
        )
        if self.configuration.polymorphic_ctype != expected_content_type:
            raise ValidationError(
                {
                    "configuration": _(
                        "Selected plugin does not correspond "
                        "to type of linked configuration."
                    )
                }
            )

    def __str__(self):
        return f"{self.get_app_label_display()}: {self.get_state_display()}"

    @property
    def app_config(self) -> PluginAppConfig:
        return apps.app_configs[self.app_label]


__all__ = ["Plugin"]
