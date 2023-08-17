from django.db import models

from apps.utils.models import BaseTimestampedModel


"""
day_index   from_   to_     enabled
0           08:00   12:00   True
0           14:00   14:00
1           08:00   12:00
"""


class OpenHours(BaseTimestampedModel):
    section = models.ForeignKey(
        "sections.Section",
        on_delete=models.CASCADE,
        related_name="open_hours",
    )

    day_index = models.PositiveSmallIntegerField(
        choices=enumerate(range(7)),
    )
    from_time = models.TimeField()
    to_time = models.TimeField()

    enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = "open hours"
        verbose_name_plural = "open hours"
        ordering = ("day_index", "from_time")
