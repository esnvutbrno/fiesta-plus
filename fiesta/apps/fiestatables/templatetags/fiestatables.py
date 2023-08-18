from __future__ import annotations

from django import template
from django.urls import reverse
from django_tables2 import tables

from apps.fiestatables.columns import SelectionColumn

register = template.Library()


@register.filter
def selection_action_button_text(table: tables.Table):
    selection_col: SelectionColumn | None = next(
        (c.column for c in table.columns.columns.values() if isinstance(c.column, SelectionColumn)), None
    )

    return selection_col.action_button_text if selection_col else None


@register.filter
def selection_action_url(table: tables.Table, placeholder: str):
    selection_col: SelectionColumn | None = next(
        (c.column for c in table.columns.columns.values() if isinstance(c.column, SelectionColumn)), None
    )

    return reverse(selection_col.action_url_name, args=(placeholder,)) if selection_col else None
