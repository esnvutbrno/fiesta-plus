from __future__ import annotations

from operator import attrgetter

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Max
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_editorjs_fields import EditorJsJSONField
from mptt.models import TreeForeignKey

from apps.utils.models.base import BaseTreeModel


class Page(BaseTreeModel):
    LEVEL_SLUG_DIVIDER = "/"

    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        db_index=True,
        verbose_name=_("parent page"),
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
    slug = models.SlugField(
        verbose_name=_("url slug"),
    )
    slug_path = models.CharField(
        max_length=128, editable=False, null=False, default="", verbose_name=_("path from slugs in page tree")
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
            # TODO: probably not needed
            models.UniqueConstraint("section", "slug", name="pages_slug_section_page_unique"),
        ]

    class MPTTMeta:
        order_insertion_by = ("order", "title")
        parent_attr = "parent"

    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self) -> str:
        return self.section.section_base_url(None) + reverse("pages:single-page", kwargs=dict(slug=self.slug_path))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        current_path = Page.LEVEL_SLUG_DIVIDER.join(map(attrgetter("slug"), self.get_ancestors(include_self=True)))
        if current_path != self.slug_path:
            self.slug_path = current_path
            super().save(update_fields=["slug_path"])


@receiver(pre_save, sender=Page)
def set_order(sender, instance: Page, **kwargs):
    if not instance.order:
        instance.order = (
            Page.objects.filter(section=instance.section).aggregate(Max("order")).get("order__max") or 0 + 1
        )
