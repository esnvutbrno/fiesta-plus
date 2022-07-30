from django.contrib.postgres.forms import SimpleArrayField
from django.forms import CheckboxSelectMultiple


class ChoicedArrayField(SimpleArrayField):
    widget_class = CheckboxSelectMultiple

    def prepare_value(self, value):
        # skip mgic with delimiter, keep it as list
        return value

    def __init__(self, base_field, *args, **kwargs):
        self.widget = self.widget_class(choices=base_field.choices)

        super().__init__(base_field, *args, **kwargs)
