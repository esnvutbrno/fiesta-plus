from __future__ import annotations

from django.core.exceptions import ValidationError
from django.forms import modelform_factory

from apps.fiestaforms.forms import BaseModelForm
from apps.plugins.models import BasePluginConfiguration
from apps.sections.models import Section
from apps.sections.services.sections_plugins_validator import SectionPluginsValidator


def get_plugin_configuration_form(configuration: BasePluginConfiguration, for_section: Section) -> type[BaseModelForm]:
    class BaseConfigurationForm(BaseModelForm):
        template_name = "sections/parts/plugin_configuration_form.html"

        def _post_clean(self):
            super()._post_clean()

            try:
                SectionPluginsValidator.for_changed_conf(
                    section=for_section,
                    conf=self.instance,
                ).check_validity()
            except ValidationError as e:
                self.add_error(None, e)

    return modelform_factory(
        configuration.__class__,
        form=BaseConfigurationForm,
        # managed by fiesta/admins
        exclude=("name", "section", "shared"),
    )
