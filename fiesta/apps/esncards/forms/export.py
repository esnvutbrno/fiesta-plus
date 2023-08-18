from __future__ import annotations

from django.forms import HiddenInput, ModelMultipleChoiceField

from apps.esncards.models import ESNcardApplication
from apps.esncards.models.export import Export
from apps.fiestaforms.forms import BaseModelForm


class NewExportForm(BaseModelForm):
    applications = ModelMultipleChoiceField(
        ESNcardApplication.objects.none(),
        required=True,
        widget=HiddenInput(),
    )

    class Meta:
        model = Export
        fields = ("applications",)
