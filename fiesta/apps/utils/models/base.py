from uuid import uuid4

from django.db import models
from django.db.models import UUIDField
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from polymorphic.models import PolymorphicModel


class BaseModel(models.Model):
    """Base model with UUID primary key."""

    id = UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True


class BaseTimestampedModel(BaseModel):
    """Base model with stored creation and last modification date."""

    created = CreationDateTimeField(_("created"))
    modified = ModificationDateTimeField(_("modified"))

    class Meta:
        abstract = True
        get_latest_by = "modified"
        ordering = ("-modified", "-created")


class BasePolymorphicModel(PolymorphicModel):
    """Base model for polymorphic usages."""

    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    created = CreationDateTimeField(_("created"))
    modified = ModificationDateTimeField(_("modified"))

    class Meta:
        abstract = True
        get_latest_by = "modified"
        ordering = ("-modified", "-created")
