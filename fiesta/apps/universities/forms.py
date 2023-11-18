from __future__ import annotations

from apps.fiestaforms.forms import BaseModelForm
from apps.universities.models import Faculty, University


class UniversityForm(BaseModelForm):
    class Meta:
        model = University
        fields = (
            "name",
            "abbr",
            "country",
        )


class FacultyForm(BaseModelForm):
    class Meta:
        model = Faculty
        fields = (
            "name",
            "abbr",
        )
