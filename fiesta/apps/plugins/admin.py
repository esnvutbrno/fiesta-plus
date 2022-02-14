from django.contrib import admin
from django.contrib.admin import display
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext as _
from polymorphic.admin import PolymorphicChildModelFilter, PolymorphicParentModelAdmin, PolymorphicChildModelAdmin

from apps.plugins.models import BasePluginConfiguration, Plugin


@admin.register(Plugin)
class PluginAdmin(admin.ModelAdmin):
    list_display = ["section", "app_label", "state", "configuration_edit", "modified"]
    list_filter = ["section", "app_label", "state"]

    @display(
        description=_("Configuration"),
        ordering="configuration",
    )
    def configuration_edit(self, obj: Plugin):
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

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('configuration')

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


class BaseChildConfigurationAdmin(PolymorphicChildModelAdmin):
    base_model = BasePluginConfiguration
    show_in_index = True

    list_display = ['name', 'plugin__section', 'plugin__state']
    list_filter = ['plugin__section', 'plugin__state']

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        return qs.select_related('plugin', 'plugin__section')

    @display
    def plugin__section(self, conf: BasePluginConfiguration):
        return conf.plugin.section

    @display
    def plugin__state(self, conf: BasePluginConfiguration):
        return conf.plugin.get_state_display()
