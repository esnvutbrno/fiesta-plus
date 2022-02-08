from functools import wraps
from typing import Type

from django.views import View
from django.utils.translation import gettext_lazy as _


def with_breadcrumb(title: str):
    """
    Class decorator to register breadcrumbs for common views.
    Used like:

    @with_with_breadcrumb(_('My view'))
    class MyView(...):
        ...
    """

    @wraps(with_breadcrumb)
    def inner(view_klass: Type[View]):
        view_klass.title = title
        return view_klass

    return inner


def with_object_breadcrumb(prefix: str = _('Detail')):
    """
    Class decorator to register breadcrumbs for detail views.
    Used like:

    @with_object_breadcrumb()
    class MyDetailView(...):
        ...
    """

    @wraps(with_breadcrumb)
    def inner(view_klass: Type[View]):
        view_klass.title = property(lambda s: f'{prefix}: {str(s.object)}')
        return view_klass

    return inner
