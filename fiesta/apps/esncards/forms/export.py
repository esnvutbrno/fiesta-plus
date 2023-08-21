from __future__ import annotations

from django.forms import ModelMultipleChoiceField, MultipleHiddenInput
from django.utils.translation import gettext_lazy as _

from apps.esncards.models import ESNcardApplication
from apps.esncards.models.export import Export
from apps.fiestaforms.forms import BaseModelForm


class NewExportForm(BaseModelForm):
    instance: Export
    submit_text = _("Accept and Generate")

    applications = ModelMultipleChoiceField(
        ESNcardApplication.objects.none(),
        required=True,
        widget=MultipleHiddenInput(),
    )

    def save(self, commit=True):
        export = super().save(commit=commit)

        self.cleaned_data["applications"].update(
            export=export,
            state=ESNcardApplication.State.ACCEPTED,
        )

        return export

    class Meta:
        model = Export
        fields = ("applications",)
