from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Max
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_editorjs_fields import EditorJsJSONField
from django_extensions.db.fields import AutoSlugField
from mptt.models import TreeForeignKey

from apps.plugins.middleware.plugin import HttpRequest
from apps.utils.models.base import BaseTreeModel


class Page(BaseTreeModel):
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )

    section = models.ForeignKey(
        "sections.Section",
        related_name="pages",
        verbose_name=_("section"),
        on_delete=models.RESTRICT,
        db_index=True,
    )

    title = models.CharField(
        max_length=128,
        verbose_name=_("page title"),
    )
    slug = AutoSlugField(
        populate_from="title",
        verbose_name=_("url slug"),
    )
    content = EditorJsJSONField(
        verbose_name=_("content"),
    )
    order = models.PositiveSmallIntegerField(
        verbose_name=_("order of display"),
        blank=True,
        null=False,
    )
    default = models.BooleanField(
        verbose_name=_("default page"),
        default=None,
        null=True,
    )

    def clean(self):
        if self.parent and self.parent.section != self.section:
            raise ValidationError(_("Cannot set page to tree of another section."))

    class Meta:
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")
        ordering = (
            "order",
            "title",
        )
        constraints = [
            models.UniqueConstraint("section", "default", name="pages_default_section_page_unique"),
        ]

    class MPTTMeta:
        order_insertion_by = ("order", "title")
        parent_attr = "parent"

    def __str__(self):
        return f"{self.title}"

    def page_url(self, request: HttpRequest) -> str:
        return reverse("pages:single-page", kwargs=dict(slug=self.slug))


@receiver(pre_save, sender=Page)
def set_order(sender, instance: Page, **kwargs):
    if not instance.order:
        instance.order = (
            Page.objects.filter(section=instance.section).aggregate(Max("order")).get("order__max") or 0 + 1
        )
