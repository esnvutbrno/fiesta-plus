from __future__ import annotations

import enum

from django import template
from django.forms import BoundField

from apps.fiestaforms.forms import BaseForm, BaseModelForm

register = template.Library()


@register.filter
def bf_type(bf: BoundField) -> str:
    return getattr(
        bf.field.widget,
        "input_type",
        "textarea" if "Textarea" in bf.field.widget.__class__.__name__ else "unknown",
    )


@register.filter
def field_modifier(bf: BoundField):
    # to notify tailwind
    return {
        "checkbox": "Forms__field--checkbox",
        "date": "Forms__field--date",
        "tel": "Forms__field--tel",
        "datetime-local": "Forms__field--datetime-local",
        "email": "Forms__field--email",
        "file": "Forms__field--file",
        "password": "Forms__field--password",
        "select": "Forms__field--select",
        "text": "Forms__field--text",
        "textarea": "Forms__field--textarea",
        "unknown": "Forms__field--unknown",
    }.get(bf_type(bf))


@register.filter
def as_widget_field(bf: BoundField):
    # to notify tailwind
    ext_class = {
        "checkbox": "Forms__checkbox",
        "email": "Forms__email",
        "tel": "Forms__tel",
        "file": "Forms__file",
        "password": "Forms__password",
        "select": "Forms__select",
        "text": "Forms__text",
        "url": "Forms__text",
        "textarea": "Forms__textarea",
        "number": "Forms__number",
        "date": "Forms__date",
        "datetime-local": "Forms__datetime-local",
        "radio": "Forms__radio",
        "unknown": "Forms__unknown",
    }
    return bf.as_widget(attrs={"class": f"Forms__input {ext_class[bf_type(bf)]}"})


@register.filter
def as_label(bf: BoundField):
    input_type = getattr(bf.field.widget, "input_type", "unknown")
    return bf.label_tag(attrs={"class": f"Forms__label Forms__label--{input_type} "})


@register.filter
def with_class(bf: BoundField, klass: str):
    return bf.as_widget(
        attrs={
            "class": klass,
        }
    )


@register.filter
def get_form_classes(form: BaseForm | BaseModelForm):
    # for generic forms, which does not have the base form class
    base_form_class_name = (
        form.base_form_class.__name__.lower() if hasattr(form, "base_form_class") else form.__class__.__name__.lower()
    )

    return f"Forms__form Forms__form--{base_form_class_name} Forms__form--{form.__class__.__name__.lower()} "


@register.filter
def name_for_select_choice(bf: BoundField, choice: enum.Enum) -> str:
    # w: RadioSelect = f.widget
    return bf.name
    # i = next((i for i, (v, _) in enumerate(f.choices) if v == choice), None)

    # return bf.html_initial_id + w.id_for_label(
    #     bf.name,
    #     i,
    # )
