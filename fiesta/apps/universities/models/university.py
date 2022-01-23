from django.db import models

from apps.utils.models import BaseTimestampedModel


class University(BaseTimestampedModel):
    name = models.CharField(max_length=128)
    abbreviation = models.SlugField(max_length=16)


#
# class Section(BaseTimestampedModel):
#     name = models.CharField(
#         max_length=64,
#         unique=True,
#     )
#
#     general_email = models.EmailField(
#         blank=True,
#         null=True,
#     )
#
#     founding = models.DateField()


__all__ = ["University"]
