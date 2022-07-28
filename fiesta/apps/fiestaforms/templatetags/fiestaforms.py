from __future__ import annotations

from django import template
from django.forms import BoundField

from apps.fiestaforms.forms import BaseForm, BaseModelForm

register = template.Library()


@register.filter
def bf_type(bf: BoundField) -> str:
    return getattr(
        bf.field.widget,
        "input_type",
        "textarea" if "Textarea" in bf.field.widget.__class__.__name__ else "unknown"
    )


@register.filter
def field_modifier(bf: BoundField):
    # to notify tailwind
    return dict(
        select='Forms__field--select',
        text='Forms__field--text',
        file='Forms__field--file',
        textarea='Forms__field--textarea',
        unknown='Forms__field--unknown',
    ).get(bf_type(bf))


@register.filter
def as_widget_field(bf: BoundField):
    # to notify tailwind
    ext_class = dict(
        select='Forms__select',
        text='Forms__text',
        file='Forms__file',
        textarea='Forms__textarea',
        unknown='Forms__unknown',
    )
    return bf.as_widget(attrs={"class": f"Forms__input {ext_class[bf_type(bf)]}"})


@register.filter
def as_label(bf: BoundField):
    input_type = getattr(bf.field.widget, "input_type", "unknown")
    return bf.label_tag(
        attrs={"class": f"Forms__label " f"Forms__label--{input_type} "}
    )


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
        form.base_form_class.__name__.lower()
        if hasattr(form, "base_form_class")
        else form.__class__.__name__.lower()
    )

    return (
        f"Forms__form "
        f"Forms__form--{base_form_class_name} "
        f"Forms__form--{form.__class__.__name__.lower()} "
    )
