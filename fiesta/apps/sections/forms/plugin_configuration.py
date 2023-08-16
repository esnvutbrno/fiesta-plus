from __future__ import annotations

from django.forms import modelform_factory

from apps.fiestaforms.forms import BaseModelForm
from apps.plugins.models import BasePluginConfiguration


def get_plugin_configuration_form(configuration: BasePluginConfiguration) -> type[BaseModelForm]:
    class BaseConfigurationForm(BaseModelForm):
        template_name = "sections/parts/plugin_configuration_form.html"

    return modelform_factory(
        configuration.__class__,
        form=BaseConfigurationForm,
        # managed by fiesta/admins
        exclude=("name", "section", "shared"),
    )
