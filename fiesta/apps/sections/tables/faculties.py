from __future__ import annotations

from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_tables2 import Column, tables

from apps.universities.models import Faculty


class UniversityFacultiesTable(tables.Table):
    name = Column(
        verbose_name=_("Name"),
        linkify=("sections:update-section-faculty", {"pk": tables.Accessor("pk")}),
        # TODO: probably extract to constant in fiestatables
        attrs={"a": {"x-data": lambda: "modal($el.href)", "x-bind": "bind"}},
    )
    abbr = Column(
        verbose_name=_("Abbreviation"),
    )

    members_count = Column(
        verbose_name=_("Members"),
        linkify=lambda record: reverse("sections:section-members") + f"?user__profile__faculty={record.pk}",
    )
    internationals_count = Column(
        verbose_name=_("Internationals"),
        linkify=lambda record: reverse("sections:section-internationals") + f"?user__profile__faculty={record.pk}",
    )
    users_count = Column(
        verbose_name=_("Users total*"),
        attrs={"th": {"title": _("Including people from other sections.")}},
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

        empty_text = _("No related faculties.")
