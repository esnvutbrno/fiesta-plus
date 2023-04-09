from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _
from django_editorjs_fields import EditorJsJSONField
from django_extensions.db.fields import AutoSlugField

from apps.utils.models import BaseTimestampedModel


class Page(BaseTimestampedModel):
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

    class Meta:
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")
