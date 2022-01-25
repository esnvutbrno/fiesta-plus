from django.db.models import Q as DjQ


class Q(DjQ):
    # https://stackoverflow.com/a/21220712/15995797
    def __xor__(self, other: DjQ) -> "Q":
        not_self = self.__invert__()
        not_other = other.__invert__()

        x = self & not_other
        y = not_self & other

        return x | y


__all__ = ["Q"]
