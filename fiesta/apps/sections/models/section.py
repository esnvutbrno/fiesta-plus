from __future__ import annotations

import typing

from django.contrib.sites.shortcuts import get_current_site
from django.db import models
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from apps.dashboard.apps import DashboardConfig
from apps.pages.apps import PagesConfig
from apps.plugins.plugin import PluginAppConfig
from apps.plugins.utils import all_plugins_mapped_to_class
from apps.utils.models import BaseTimestampedModel
from apps.utils.models.validators import validate_plain_slug_lowercase

if typing.TYPE_CHECKING:
    from apps.plugins.middleware.plugin import HttpRequest
    from apps.sections.models import SectionMembership


class Section(BaseTimestampedModel):
    name = models.CharField(
        max_length=64,
        unique=True,
        verbose_name=_("name"),
        help_text=_("Full name of section, e.g. ESN VUT Brno"),
    )
    country = CountryField(
        verbose_name=_("country"),
    )

    universities = models.ManyToManyField(
        "universities.University",
        through="sections.SectionUniversity",
        verbose_name=_("universities"),
        help_text=_("Universities, for whose this section offers services."),
    )

    code = models.SlugField(
        verbose_name=_("code"),
        help_text=_("Official code used in ESN world, especially in ESN Accounts database."),
        # TODO: remove blankness after proper migration from ESN accounts
        null=True,
        blank=True,
        unique=True,
    )

    space_slug = models.SlugField(
        verbose_name=_("space slug"),
        help_text=_("Slug used for defining section spaces as URL subdomains."),
        unique=True,
        validators=[validate_plain_slug_lowercase],
    )

    class SystemState(TextChoices):
        ENABLED = "enabled", _("Enabled")
        PAUSED = "paused", _("Paused")
        DISABLED = "disabled", _("Disabled")

    system_state = models.CharField(
        max_length=16,
        choices=SystemState.choices,
        default=SystemState.DISABLED,
        verbose_name=_("state in this system"),
        help_text=_("Marks state of the section in context of usage of this system."),
    )

    class Meta:
        verbose_name = _("ESN section")
        verbose_name_plural = _("ESN sections")
        ordering = ("name",)

    def __str__(self):
        return self.name

    def section_base_url(self, request: HttpRequest):
        site = get_current_site(request)

        return f"//{self.space_slug}.{site.domain}"

    def section_home_url(self, for_membership: SectionMembership = None) -> str | None:
        from apps.plugins.models import Plugin

        enabled_plugins = self.plugins.filter(
            state__in=(
                (Plugin.State.ENABLED,)
                + ((Plugin.State.PRIVILEGED_ONLY,) if for_membership and for_membership.is_privileged else ())
            ),
        ).values_list(
            "app_label",
            flat=True,
        )

        pages_app = all_plugins_mapped_to_class().get(PagesConfig)
        dashboard_app = all_plugins_mapped_to_class().get(DashboardConfig)

        target_app: PluginAppConfig | None = None

        if for_membership and dashboard_app and dashboard_app.label in enabled_plugins:
            target_app = dashboard_app
        elif not for_membership and pages_app and pages_app.label in enabled_plugins:
            target_app = pages_app

        # TODO: what to do if user is logged and dashboard is not available?
        return f"/{target_app.url_prefix}" if target_app else None


class SectionUniversity(BaseTimestampedModel):
    section = models.ForeignKey(
        "sections.Section",
        on_delete=models.RESTRICT,
        verbose_name=_("ESN section"),
        db_index=False,
    )
    university = models.ForeignKey(
        "universities.University",
        on_delete=models.CASCADE,
        verbose_name=_("university"),
        db_index=False,
    )

    class Meta:
        verbose_name = _("Section university")
        verbose_name_plural = _("Section universities")
        unique_together = (("section", "university"),)

    def __str__(self):
        return f"{self.section} - {self.university}"


__all__ = ["Section", "SectionUniversity"]
