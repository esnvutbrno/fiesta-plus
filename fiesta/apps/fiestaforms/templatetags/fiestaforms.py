from django.forms import BoundField
from django import template

register = template.Library()


@register.filter
def as_widget_field(field: BoundField):
    return field.as_widget(attrs={
        'class': f"Forms__{field.field.widget.input_type}"}
    )


@register.filter
def as_label(field: BoundField):
    return field.label_tag(
        attrs={'class': f"Forms__label Forms__label--{field.field.widget.input_type}"}
    )
