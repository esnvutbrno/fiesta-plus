from __future__ import annotations

from django.test import TestCase

from apps.buddy_system.models import BuddySystemConfiguration
from apps.notifications.services.plugin_config import get_plugin_configuration
from apps.plugins.models import Plugin
from apps.utils.factories.sections import KnownSectionFactory


class GetPluginConfigurationTestCase(TestCase):
    def test_returns_configuration_for_real_enabled_plugin(self):
        """
        End-to-end: a real Plugin + BuddySystemConfiguration row (no mocking) must be
        found via the actual section.plugins relation, not a nonexistent attribute.
        """
        section = KnownSectionFactory()
        config = BuddySystemConfiguration.objects.create(section=section)
        Plugin.objects.create(section=section, app_label="buddy_system", configuration=config)

        found = get_plugin_configuration(section, "buddy_system")

        self.assertEqual(found, config)

    def test_returns_none_when_plugin_not_enabled(self):
        section = KnownSectionFactory()

        found = get_plugin_configuration(section, "buddy_system")

        self.assertIsNone(found)
