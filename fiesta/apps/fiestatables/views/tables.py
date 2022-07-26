from datetime import datetime

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

        return (
            f"{(datetime.now().isoformat('_', 'seconds')).replace(':', '-')}"
            f"_{self.export_name}.{export_format}"
        )
