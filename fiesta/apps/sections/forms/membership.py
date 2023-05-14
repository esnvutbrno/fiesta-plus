from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from apps.fiestaforms.forms import BaseModelForm
from apps.sections.models import SectionMembership


class ChangeMembershipStateForm(BaseModelForm):
    submit_text = _("Change")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # TODO: preselect active?

    class Meta:
        model = SectionMembership
        fields = (
            "role",
            "state",
        )
