from django.contrib.postgres.forms import SimpleArrayField
from django.forms import CheckboxSelectMultiple
from django.utils.datastructures import MultiValueDict


class DelimitedCheckboxSelectMultiple(CheckboxSelectMultiple):
    def __init__(self, *args, **kwargs):
        # Accept a `delimiter` argument, and grab it (defaulting to a comma)
        self.delimiter = kwargs.pop("delimiter", ",")
        super(DelimitedCheckboxSelectMultiple, self).__init__(*args, **kwargs)

    def render_options(self, choices, value):
        # value *should* be a list, but it might be a delimited string.
        if isinstance(
            value, str
        ):  # python 2 users may need to use basestring instead of str
            value = value.split(self.delimiter)
        return super(DelimitedCheckboxSelectMultiple, self).render_options(
            choices, value
        )

    def value_from_datadict(self, data, files, name):
        if isinstance(data, MultiValueDict):
            # Normally, we'd want a list here, which is what we get from the
            # SelectMultiple superclass, but the SimpleArrayField expects to
            # get a delimited string, so we're doing a little extra work.
            return self.delimiter.join(data.getlist(name))
        return data.get(name, None)


class ChoicedArrayField(SimpleArrayField):
    widget_class = DelimitedCheckboxSelectMultiple

    def __init__(
        self, base_field, *, delimiter=",", max_length=None, min_length=None, **kwargs
    ):
        self.widget = self.widget_class(choices=base_field.choices)
        super().__init__(
            base_field,
            delimiter=delimiter,
            max_length=max_length,
            min_length=min_length,
            **kwargs
        )
