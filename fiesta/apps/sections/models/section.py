from __future__ import annotations

import logging
import typing

from _operator import attrgetter
from django.contrib.sites.shortcuts import get_current_site
from django.db import models
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from apps.dashboard.apps import DashboardConfig
from apps.pages.apps import PagesConfig
from apps.plugins.models import Plugin
from apps.plugins.plugin import BasePluginAppConfig
from apps.plugins.utils import all_plugins_mapped_to_class
from apps.sections.models.managers.section import SectionsManager
from apps.utils.models import BaseTimestampedModel
from apps.utils.models.validators import validate_plain_slug_lowercase

if typing.TYPE_CHECKING:
    from apps.plugins.middleware.plugin import HttpRequest
    from apps.sections.models import SectionMembership

logger = logging.getLogger(__name__)


class Section(BaseTimestampedModel):
    objects = SectionsManager()

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
        db_index=True,
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

    def section_base_url(self, request: HttpRequest | None):
        site = get_current_site(request)

        return f"//{self.space_slug}.{site.domain}"

    def section_home_url(self, for_membership: SectionMembership = None) -> str | None:
        """
        Returns home URL page of a section, if available:
            - for non-members, it's always pages (if enabled, available for a current role and has default page)
            - for members, it's always dashboard (if available and enabled for a current role)
            - otherwise, None
        """
        # TODO: refactor to share code from CheckEnabledPluginsViewMixin
        plugins = (
            self.enabled_plugins_for_privileged
            if for_membership and for_membership.is_privileged
            else self.enabled_plugins
        )

        available_plugins = tuple(map(attrgetter("app_label"), plugins))

        pages_app: PagesConfig | None = all_plugins_mapped_to_class().get(PagesConfig)
        dashboard_app: DashboardConfig | None = all_plugins_mapped_to_class().get(DashboardConfig)

        target_app: BasePluginAppConfig | None = None

        if for_membership and dashboard_app and dashboard_app.label in available_plugins:
            # in active membership, dashboard is always preferred
            target_app = dashboard_app
        elif not for_membership and pages_app and pages_app.label in available_plugins:
            # for non-members, pages are preferred (if available)
            has_default_page = self.pages.filter(default=True).exists()
            if has_default_page:
                target_app = pages_app

        if not target_app:
            logger.warning(
                "No home URL found for section %s to membership %s.",
                self,
                for_membership,
            )

        return f"/{target_app.url_prefix}" if target_app else None

    # prefetched for request.in_space_of_section
    enabled_plugins: list[Plugin]

    # prefetched for request.in_space_of_section
    enabled_plugins_for_privileged: list[Plugin]

    # only typing of related manager
    buddy_system_requests: models.QuerySet
    pickup_system_requests: models.QuerySet


class SectionUniversity(BaseTimestampedModel):
    section = models.ForeignKey(
        "sections.Section",
        on_delete=models.RESTRICT,
        verbose_name=_("ESN section"),
        related_name="section_universities",
        db_index=False,
    )
    university = models.ForeignKey(
        "universities.University",
        on_delete=models.CASCADE,
        verbose_name=_("university"),
        related_name="university_sections",
        db_index=False,
    )

    class Meta:
        verbose_name = _("Section university")
        verbose_name_plural = _("Section universities")
        unique_together = (("section", "university"),)

    def __str__(self):
        return f"{self.section} - {self.university}"


__all__ = ["Section", "SectionUniversity"]
