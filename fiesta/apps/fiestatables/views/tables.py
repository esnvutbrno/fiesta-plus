import contextlib
from datetime import datetime

from django.db.models import QuerySet
from django.utils.text import slugify
from django_tables2 import SingleTableMixin, LazyPaginator
from django_tables2.export import ExportMixin, TableExport

from apps.fiestatables.views.htmx import HtmxTableMixin


class FiestaTableMixin(HtmxTableMixin, SingleTableMixin, ExportMixin):
    paginate_by = 20
    paginator_class = LazyPaginator
    template_name = "fiestatables/page.html"

    export_formats = (TableExport.CSV, TableExport.JSON, TableExport.XLSX)

    def get_export_filename(self, export_format):
        # TODO: get QS and rename the output
        export_name = self.export_name

        data: QuerySet | list = self.get_table_data()

        with contextlib.suppress(AttributeError, TypeError):
            export_name = slugify(data.model._meta.verbose_name_plural.lower())

        return (
            f"{(datetime.now().isoformat('_', 'seconds')).replace(':', '-')}"
            f"_{export_name}.{export_format}"
        )
