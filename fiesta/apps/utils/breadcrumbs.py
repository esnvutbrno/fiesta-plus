from __future__ import annotations

from functools import wraps
from typing import Type, NamedTuple, Callable

from django.db.models import Model
from django.http import HttpRequest
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _
from django.views import View


class BreadcrumbItem(NamedTuple):
    title: str  # or lazy str
    url: str

    def __str__(self):
        return force_str(self.title)


def push_breadcrumb_item(request: HttpRequest, item: str | BreadcrumbItem):
    """
    Adds breadcrumb item to current request context.
    """
    try:
        request.titles.append(item)
    except AttributeError:
        request.titles = [item]


def with_breadcrumb(title: str, *, url_name: str = None):
    """
    Class decorator to register breadcrumbs for common views.
    Used like:

    @with_with_breadcrumb(_('My view'))
    class MyView(...):
        ...
    """

    @wraps(with_breadcrumb)
    def inner(view_klass: Type[View]):
        @wraps(view_klass.dispatch)
        def dispatch(self, request, *args, **kwargs):
            _title_to_append = (
                BreadcrumbItem(title, reverse(url_name)) if url_name else title
            )

            push_breadcrumb_item(request=request, item=_title_to_append)

            return super(self.__class__, self).dispatch(request, *args, **kwargs)

        view_klass.dispatch = dispatch
        return view_klass

    return inner


def with_object_breadcrumb(prefix: str = None, getter: Callable[[Model], str] = None):
    """
    Class decorator to register breadcrumbs for detail views.
    Used like:

    @with_object_breadcrumb()
    class MyDetailView(...):
        ...
    """

    @wraps(with_breadcrumb)
    def inner(view_klass: Type[View]):
        @wraps(view_klass.dispatch)
        def dispatch(self, request, *args, **kwargs):
            response = super(self.__class__, self).dispatch(request, *args, **kwargs)

            push_breadcrumb_item(
                request=request,
                item=f"{prefix or _('Detail')}: {(getter or str)(self.object)}",
            )
            return response

        view_klass.dispatch = dispatch
        return view_klass

    return inner
