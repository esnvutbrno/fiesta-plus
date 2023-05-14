from __future__ import annotations

import contextlib

from django.db.models import QuerySet
from django.utils import timezone
from django.utils.text import slugify
from django_filters.views import FilterView
from django_tables2 import LazyPaginator, MultiTableMixin, SingleTableMixin
from django_tables2.export import ExportMixin, TableExport

from apps.fiestatables.views.htmx import HtmxTableMixin


class FiestaExportMixin(ExportMixin):
    export_formats = (TableExport.CSV, TableExport.JSON, TableExport.XLSX)

    def get_export_filename(self, export_format):
        export_name = self.export_name

        data: QuerySet | list = self.get_table_data()

        with contextlib.suppress(AttributeError, TypeError):
            export_name = slugify(data.model._meta.verbose_name_plural.lower())

        return f"{(timezone.now().isoformat('_', 'seconds')).replace(':', '-')}_{export_name}.{export_format}"


class FiestaSingleTableMixin(HtmxTableMixin, SingleTableMixin, FiestaExportMixin):
    paginate_by = 20
    paginator_class = LazyPaginator
    template_name = "fiestatables/page.html"


class FiestaMultiTableMixin(HtmxTableMixin, MultiTableMixin, FiestaExportMixin):
    paginate_by = 20
    paginator_class = LazyPaginator
    template_name = "fiestatables/page.html"


class PreprocessQuerySetMixin:
    select_related = None
    prefetch_related = None

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        if self.select_related is not None:
            qs = qs.select_related(*self.select_related)

        if self.prefetch_related is not None:
            qs = qs.prefetch_related(*self.prefetch_related)

        return qs


class FiestaTableView(PreprocessQuerySetMixin, FiestaSingleTableMixin, FilterView):
    pass


class FiestaMultiTableView(PreprocessQuerySetMixin, FiestaMultiTableMixin, FilterView):
    pass
