from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from apps.utils.models import BaseTimestampedModel


class SectionMembership(BaseTimestampedModel):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.RESTRICT,
        related_name="memberships",
        verbose_name=_("user"),
        db_index=True,
    )
    section = models.ForeignKey(
        "sections.Section",
        on_delete=models.RESTRICT,
        related_name="memberships",
        verbose_name=_("section"),
        db_index=True,
    )

    class Role(models.TextChoices):
        INTERNATIONAL = "international", _("International")
        MEMBER = "member", _("Member")
        EDITOR = "editor", _("Editor")
        ADMIN = "admin", _("Admin")

        @property
        def is_privileged(self):
            return self in (self.__class__.EDITOR, self.__class__.ADMIN)

    role = models.CharField(
        max_length=16,
        choices=Role.choices,
        verbose_name=_("section role"),
    )

    class State(models.TextChoices):
        INACTIVE = "inactive", _("Inactive")
        ACTIVE = "active", _("Active")
        SUSPENDED = "suspended", _("Suspended")

    state = models.CharField(
        max_length=16,
        choices=State.choices,
        verbose_name=_("membership state"),
    )

    # TODO: add flag to signalize, if membership has been added from ESN Accounts

    class Meta:
        verbose_name = _("section membership")
        verbose_name_plural = _("section memberships")
        unique_together = ("user", "section")

    def __str__(self):
        return f"{self.section}: {self.get_role_display()} {self.user} ({self.get_state_display()})"

    @property
    def available_plugins_filter(self) -> Q:
        # on context of Queryset[Plugin]
        from apps.plugins.models import Plugin

        avaiable_states = (
            (Plugin.State.ENABLED, Plugin.State.PRIVILEGED_ONLY)
            if self.Role(self.role).is_privileged else
            (Plugin.State.ENABLED,)
        )

        return Q(section=self.section, state__in=avaiable_states)


__all__ = ["SectionMembership"]
