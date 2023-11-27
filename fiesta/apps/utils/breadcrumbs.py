from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import NamedTuple

from django.db.models import Model
from django.http import HttpRequest
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.functional import lazy
from django.utils.translation import gettext_lazy as _
from django.views import View


class BreadcrumbItem(NamedTuple):
    title: str  # or lazy str
    url: str

    def __str__(self):
        return force_str(self.title)


def push_breadcrumb_item(request: HttpRequest, item: str | BreadcrumbItem | Callable[[], BreadcrumbItem]):
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
    def inner(view_klass: type[View]):
        old_dispatch = view_klass.dispatch

        @wraps(view_klass.dispatch)
        def dispatch(self, request, *args, **kwargs):
            _title_to_append = BreadcrumbItem(title, reverse(url_name)) if url_name else title

            push_breadcrumb_item(request=request, item=_title_to_append)

            return old_dispatch(self, *args, request=request, **kwargs)

        view_klass.dispatch = dispatch
        return view_klass

    return inner


USE_DEFAULT_PREFIX = object()


def with_object_breadcrumb(prefix: str | None = USE_DEFAULT_PREFIX, getter: Callable[[Model], str] = None):
    """
    Class decorator to register breadcrumbs for detail views.
    Used like:

    @with_object_breadcrumb()
    class MyDetailView(...):
        ...
    """

    @wraps(with_object_breadcrumb)
    def inner(view_klass: type[View]):
        old_dispatch = view_klass.dispatch

        @wraps(view_klass.dispatch)
        def dispatch(self, request, *args, **kwargs):
            lazy_title = lambda: (
                f"{(_('Detail') + ': ') if prefix is USE_DEFAULT_PREFIX else (prefix or '')}"
                f"{(getter or str)(self.object)}"
            )
            push_breadcrumb_item(
                request=request,
                item=lazy(lazy_title, str),
            )
            return old_dispatch(self, *args, request=request, **kwargs)

        view_klass.dispatch = dispatch
        return view_klass

    return inner


def with_callable_breadcrumb(getter: Callable[[View], BreadcrumbItem]):
    """
    Used like:

    @with_callable_breadcrumb(lambda view: BreadcrumbItem(...))
    class MyDetailView(...):
        ...
    """

    @wraps(with_callable_breadcrumb)
    def inner(view_klass: type[View]):
        old_dispatch = view_klass.dispatch

        @wraps(view_klass.dispatch)
        def dispatch(self, request, *args, **kwargs):
            def lazy_getter():
                return getter(self)

            push_breadcrumb_item(
                request=request,
                item=lazy_getter,
            )
            return old_dispatch(self, *args, request=request, **kwargs)

        view_klass.dispatch = dispatch
        return view_klass

    return inner


def with_plugin_home_breadcrumb(f):
    return with_callable_breadcrumb(
        lambda view: BreadcrumbItem(
            view.request.plugin.app_config.verbose_name, view.request.plugin.app_config.reverse("index")
        )
    )(f)
