from __future__ import annotations

from django.contrib.postgres.fields import ArrayField
from django.utils.encoding import force_str
from django.utils.hashable import make_hashable


class ArrayFieldWithDisplayableChoices(ArrayField):
    def contribute_to_class(self, cls, name, private_only=False):
        super().contribute_to_class(cls, name, private_only)

        def get_array_display(instance):
            choices_dict = dict(make_hashable(self.base_field.flatchoices))
            return [
                force_str(choices_dict.get(make_hashable(value), value), strings_only=True)
                for value in getattr(instance, self.attname)
            ]

        if "get_%s_display" % self.name not in cls.__dict__:
            setattr(
                cls,
                "get_%s_display" % self.name,
                get_array_display,
            )
