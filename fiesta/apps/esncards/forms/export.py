from __future__ import annotations

from django.forms import HiddenInput, ModelMultipleChoiceField
from django.utils.translation import gettext_lazy as _

from apps.esncards.models import ESNcardApplication
from apps.esncards.models.export import Export
from apps.fiestaforms.forms import BaseModelForm


class NewExportForm(BaseModelForm):
    submit_text = _("Accept and Generate")

    applications = ModelMultipleChoiceField(
        ESNcardApplication.objects.none(),
        required=True,
        widget=HiddenInput(),
    )

    class Meta:
        model = Export
        fields = ("applications",)
