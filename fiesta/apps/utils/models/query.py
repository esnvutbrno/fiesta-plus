from django.core.exceptions import ValidationError
from django.db.models import Model, Q as DjangoQ, QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404


class Q(DjangoQ):
    # https://stackoverflow.com/a/21220712/15995797
    def __xor__(self, other: DjangoQ) -> "Q":
        not_self = self.__invert__()
        not_other = other.__invert__()

        x = self & not_other
        y = not_self & other

        return x | y


def get_single_object_or_none(klass: QuerySet | type[Model], *args, **kwargs):
    try:
        return get_object_or_404(*args, klass=klass, **kwargs)
    except (Http404, klass.MultipleObjectsReturned, ValidationError):
        return None


__all__ = ["Q", "get_single_object_or_none"]
