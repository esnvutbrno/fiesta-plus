from typing import Type

from django.contrib import admin
from django.contrib.admin import display
from django.contrib.contenttypes.models import ContentType
from django.db.models import Prefetch, QuerySet
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.utils.translation import gettext as _
from polymorphic.admin import (
    PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter,
    PolymorphicParentModelAdmin,
)

from apps.plugins.models import BasePluginConfiguration, Plugin
from apps.utils.utils import all_non_abstract_sub_models


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
        return super().get_queryset(request).select_related("configuration")

    # TODO: make configuration form field dependent on selected configuration
    # https://django-autocomplete-light.readthedocs.io/en/master/tutorial.html
    # Filtering results based on the value of other fields in the form

    # TODO: relating to django-polymorphic docs, UUID PK should not work
    # but I haven't encoutered any issue with this, so idk
    # solution: https://github.com/django-polymorphic/django-polymorphic/issues/81#issuecomment-112152701


def prefetch_for_base_configuration(qs: QuerySet):
    plugins_qs = Plugin.objects.select_related("section")
    return qs.prefetch_related(Prefetch("plugins", queryset=plugins_qs)).select_related(
        "section",
        "polymorphic_ctype",
    )


@display(description=_("Used in plugins"))
def plugins__section(self, conf: BasePluginConfiguration):
    return format_html_join(
        ", ",
        '<a href="{}">{}</a>',
        (
            (
                reverse("admin:plugins_plugin_change", args=[p.id]),
                f"{p.section} ({p.get_state_display()})",
            )
            for p in conf.plugins.all()
        ),
    )


@admin.register(BasePluginConfiguration)
class BasePluginConfigurationAdmin(PolymorphicParentModelAdmin):
    list_display = [
        "name",
        "section",
        "shared",
        "plugins__section",
        "polymorphic_ctype",
    ]
    list_filter = [
        PolymorphicChildModelFilter,
        "shared",
        "section",
    ]

    def get_child_models(self) -> tuple[Type[BasePluginConfiguration]]:
        return all_non_abstract_sub_models(BasePluginConfiguration)

    plugins__section = plugins__section

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        return prefetch_for_base_configuration(qs)


class BaseChildConfigurationAdmin(PolymorphicChildModelAdmin):
    base_model = BasePluginConfiguration
    show_in_index = True

    list_display = ["name", "plugins__section"]
    list_filter = ["plugins__section"]

    base_fieldsets = ((None, {"fields": ("name", "section", "shared")}),)

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        return prefetch_for_base_configuration(qs)

    @property
    def extra_fieldset_title(self):
        return _("Specific {}").format(self.model._meta.verbose_name)

    plugins__section = plugins__section
