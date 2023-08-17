from apps.fiestaforms.forms import BaseModelForm
from apps.open_hours.models import OpenHours


class OpenHoursForm(BaseModelForm):
    class Meta:
        model = OpenHours
        fields = (
            "day_index",
            "from_time",
            "to_time",
            "enabled",
        )
