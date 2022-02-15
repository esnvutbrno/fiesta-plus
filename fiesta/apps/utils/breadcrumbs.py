from functools import wraps
from typing import Type

from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View

from apps.utils.templatetags.breadcrumbs import BreadcrumbTitle


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
                BreadcrumbTitle(title, reverse(url_name)) if url_name else title
            )

            request.titles = [
                _title_to_append,
            ]
            return super(self.__class__, self).dispatch(request, *args, **kwargs)

        view_klass.dispatch = dispatch
        return view_klass

    return inner


def with_object_breadcrumb(prefix: str = None):
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
            request.titles = property(
                lambda s: [
                    f"{prefix or _('Detail')}: {str(s.object)}",
                ]
            )
            return super(self.__class__, self).dispatch(request, *args, **kwargs)

        view_klass.dispatch = dispatch
        return view_klass

    return inner
