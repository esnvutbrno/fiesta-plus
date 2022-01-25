from django.db import models
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

    class Meta:
        verbose_name = _("section membership")
        verbose_name_plural = _("section memberships")
        unique_together = ("user", "section")

    def __str__(self):
        return f"{self.section}: {self.get_role_display()} {self.user} ({self.get_state_display()})"


__all__ = ["SectionMembership"]
