from __future__ import annotations

from django.db.models import Manager, Prefetch


class SectionMembershipsManager(Manager):
    def prefetch_plugins(self):
        from apps.plugins.models import Plugin

        return self.prefetch_related(
            # optimizations
            Prefetch(
                "section__plugins",
                queryset=Plugin.objects.filter(
                    state__in=(Plugin.State.ENABLED,),
                ),
                to_attr="enabled_plugins",
            ),
            Prefetch(
                "section__plugins",
                queryset=Plugin.objects.filter(
                    state__in=(Plugin.State.ENABLED, Plugin.State.PRIVILEGED_ONLY),
                ),
                to_attr="enabled_plugins_for_privileged",
            ),
        )
