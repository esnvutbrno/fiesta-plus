from __future__ import annotations

from django.urls import reverse
from django_tables2 import Column, tables

from apps.universities.models import Faculty


class UniversityFacultiesTable(tables.Table):
    name = Column()
    abbr = Column()

    members_count = Column(
        linkify=lambda record: reverse("sections:section-members") + f"?user__profile__faculty={record.pk}",
    )
    internationals_count = Column(
        linkify=lambda record: reverse("sections:section-internationals") + f"?user__profile__faculty={record.pk}",
    )

    class Meta:
        model = Faculty

        fields = ("abbr",)

        sequence = (
            "name",
            "abbr",
            "...",
        )

        attrs = dict(tbody={"hx-disable": True})
