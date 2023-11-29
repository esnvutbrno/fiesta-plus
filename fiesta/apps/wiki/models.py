from __future__ import annotations

from django.db import models


class Page(models.Model):
    file = models.CharField(primary_key=True, max_length=255, db_column="file")
    title = models.CharField(max_length=255, db_column="title")
    content_html = models.TextField(db_column="content_html")
    content_plain = models.TextField(db_column="content_plain")
    toc = models.TextField(db_column="toc")

    last_change = models.JSONField(db_column="last_change")

    class Meta:
        managed = False
        db_table = "wiki"

    def __str__(self):
        return self.title
