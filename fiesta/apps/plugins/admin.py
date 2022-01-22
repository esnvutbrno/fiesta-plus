from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext as _
from polymorphic.admin import PolymorphicChildModelFilter, PolymorphicParentModelAdmin

from apps.plugins.models import BasePluginConfiguration, Plugin


@admin.register(Plugin)
class PluginAdmin(admin.ModelAdmin):
    list_display = ["app_label", "state", "configuration_edit", "modified"]
    list_filter = ["app_label", "state"]

    @staticmethod
    def configuration_edit(obj: Plugin):
        if not obj.configuration:
            return
        ct: ContentType = obj.configuration.polymorphic_ctype

        return format_html(
            '<a href="{link}">{obj}</a>',
            link=reverse(
                f"admin:{ct.app_label}_{ct.model}_change", args=[obj.configuration_id]
            ),
            obj=str(obj.configuration),
        )

    configuration_edit.short_description = _("Configuration")
    configuration_edit.admin_order_field = "configuration"

    # TODO: make configuration form field dependent on selected configuration
    # https://django-autocomplete-light.readthedocs.io/en/master/tutorial.html
    # Filtering results based on the value of other fields in the form

    # TODO: relating to django-polymorphic docs, UUID PK should not work
    # but I haven't encoutered any issue with this, so idk
    # solution: https://github.com/django-polymorphic/django-polymorphic/issues/81#issuecomment-112152701


@admin.register(BasePluginConfiguration)
class BasePluginConfigurationAdmin(PolymorphicParentModelAdmin):
    list_display = ["name", "polymorphic_ctype"]
    list_filter = [
        PolymorphicChildModelFilter,
    ]

    child_models = BasePluginConfiguration.__subclasses__()
