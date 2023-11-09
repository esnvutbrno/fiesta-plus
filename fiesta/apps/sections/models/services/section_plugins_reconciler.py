from __future__ import annotations

import logging

from django.apps import apps
from django.db import transaction
from django.db.models import Model

from apps.plugins.utils import all_plugin_apps
from apps.sections.models import Section

logger = logging.getLogger(__name__)


class SectionPluginsReconciler:
    """Handles auto-created plugins for sections."""

    @classmethod
    @transaction.atomic
    def reconcile(cls, section: Section):
        for plugin_app in all_plugin_apps():
            if not plugin_app.auto_enabled:
                continue

            if section.plugins.filter(app_label=plugin_app.label).exists():
                continue

            from apps.plugins.models import Plugin

            conf = None

            if plugin_app.configuration_model:
                conf_model: Model = apps.get_model(plugin_app.configuration_model)

                conf, _ = conf_model.objects.get_or_create(
                    section=section,
                    shared=False,
                )

            plugin, _ = section.plugins.get_or_create(
                app_label=plugin_app.label,
                defaults=dict(
                    configuration=conf,
                    state=Plugin.State.ENABLED,
                ),
            )

            logger.info("Auto created plugin %s for section %s", plugin, section)
