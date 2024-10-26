from __future__ import annotations

from django.core.exceptions import ValidationError
from django.forms import Textarea
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User
from apps.fiestaforms.forms import BaseModelForm
from apps.fiestaforms.widgets.models import ActiveLocalMembersFromSectionWidget, UserWidget
from apps.fiestarequests.models.request import BaseRequestMatchProtocol, BaseRequestProtocol


class BaseRequestEditorForm(BaseModelForm):
    submit_text = _("Save")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["issuer"].disabled = True

        if self.instance.state != BaseRequestProtocol.State.CREATED:
            self.fields["note"].disabled = True

    class Meta:
        fields = (
            "issuer",
            "state",
            "note",
        )
        field_classes = {}
        widgets = {
            "issuer": UserWidget,
            "note": Textarea(attrs={"rows": 5}),
        }


class BaseQuickMatchForm(BaseModelForm):
    submit_text = _("Match")
    instance: BaseRequestMatchProtocol

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        fields = ("matcher",)
        widgets = {
            "matcher": ActiveLocalMembersFromSectionWidget,
        }

    def clean_matcher(self):
        matcher: User = self.cleaned_data["matcher"]

        if not matcher.profile_or_none:
            raise ValidationError(
                _("This user has not completed their profile. Please ask them to do so before matching.")
            )

        if not matcher.profile_or_none.faculty:
            raise ValidationError(_("This user has not set their faculty. Please ask them to do so or do it yourself."))

        return matcher
