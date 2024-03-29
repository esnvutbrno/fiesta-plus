from __future__ import annotations

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from django_tables2 import Column, TemplateColumn

from apps.fiestatables.columns import AvatarColumn, CountryColumn, LabeledChoicesColumn, NaturalDatetimeColumn
from apps.sections.models import SectionMembership


class SectionMembershipTable(tables.Table):
    user__full_name_official = Column(
        verbose_name=_("Member"),
        order_by=("user__last_name", "user__first_name", "user__username"),
        linkify=(
            "sections:membership-detail",
            dict(
                pk=tables.A("pk"),
            ),
        ),
        attrs=dict(a={"hx-disable": True}),  # TODO: do it properly
    )
    user__profile__picture = AvatarColumn()
    user__profile__nationality = CountryColumn(verbose_name=_("Nationality"))
    user__profile__faculty__abbr = Column(verbose_name=_("Faculty"))

    role = LabeledChoicesColumn(choices=SectionMembership.Role, verbose_name=_("Role"))

    created = NaturalDatetimeColumn(verbose_name=_("Joined"))

    state_button = TemplateColumn(
        template_name="sections/parts/change_membership_state_btn.html",
        exclude_from_export=True,
        order_by="state",
        verbose_name=_("Membership"),
    )

    class Meta:
        model = SectionMembership

        fields = ("created",)

        sequence = (
            "user__full_name_official",
            "user__profile__picture",
            "user__profile__nationality",
            "user__profile__faculty__abbr",
            "role",
            "...",
        )

        attrs = dict(tbody={"hx-disable": True})
