from django.core.exceptions import ValidationError
from django.db.models import Q as DjQ
from django.http import Http404
from django.shortcuts import get_object_or_404


class Q(DjQ):
    # https://stackoverflow.com/a/21220712/15995797
    def __xor__(self, other: DjQ) -> "Q":
        not_self = self.__invert__()
        not_other = other.__invert__()

        x = self & not_other
        y = not_self & other

        return x | y


def get_object_or_none(klass, *args, **kwargs):
    try:
        return get_object_or_404(klass=klass, *args, **kwargs)
    except (Http404, ValidationError):
        return None


__all__ = ["Q", "get_object_or_none"]
