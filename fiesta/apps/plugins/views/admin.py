from _operator import attrgetter

from dal import autocomplete
from django.apps import apps
from django.contrib.contenttypes.models import ContentType

from apps.plugins.models import BasePluginConfiguration
from apps.plugins.utils import all_plugin_apps
from apps.sections.models import Section
from apps.utils.models.query import get_object_or_none, Q
from apps.utils.request import HttpRequest


class ConfigurationAutocomplete(autocomplete.Select2QuerySetView):
    request: HttpRequest

    def get_queryset(self):
        if not self.request.user.is_staff:
            return BasePluginConfiguration.objects.none()

        # {'section': 'f8ae88b4-468a-4934-ab59-aa8036cab051', 'app_label': 'buddy_system'}
        qs = BasePluginConfiguration.objects.all()

        if section := get_object_or_none(Section, pk=self.forwarded.get("section")):
            qs = qs.filter(Q(section=section) | Q(shared=True))
        else:
            qs = qs.filter(Q(shared=True))

        if app := apps.app_configs.get(self.forwarded.get("app_label")):
            expected_content_type = ContentType.objects.get_for_model(
                apps.get_model(app.configuration_model)
            )

            qs = qs.filter(polymorphic_ctype=expected_content_type)

        return qs


class AppAutocomplete(autocomplete.Select2ListView):
    request: HttpRequest

    def get_list(self):
        exclude = {}
        if section := get_object_or_none(Section, pk=self.forwarded.get("section")):
            exclude = set(map(attrgetter("app_label"), section.plugins.all()))
        return [
            (p.label, p.verbose_name)
            for p in all_plugin_apps()
            if p.label not in exclude
        ]
